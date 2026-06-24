#!/usr/bin/env python3
"""
Evaluation harness for the ShopEase customer support agent.

Usage:
    python tests/eval.py [--api-url http://localhost:8000] --token <jwt> [options]

Options:
    --category policy|order|escalation   Filter by scenario category
    --ids P01 P02 E01 ...                Run specific scenario IDs
    --judge                              Enable LLM-as-judge scoring (requires OPENAI_API_KEY)
    --judge-model gpt-4o-mini            Model to use for judging (default: gpt-4o-mini)
    --report                             Save a JSON report to tests/eval_report.json
    --verbose / -v                       Show judge reasoning per scenario

The script:
1. Loads scenarios from tests/scenarios.json
2. For each scenario, calls POST /api/v1/chat/stream with the conversation
3. Collects streamed events (tool calls + final text)
4. Runs rule-based checks (correct tool, escalation, etc.)
5. Optionally runs LLM-as-judge scoring for response quality
6. Prints a per-scenario report + summary
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Optional

import httpx


BASE_URL = os.getenv("EVAL_API_URL", "http://localhost:8000")
SCENARIOS_FILE = os.path.join(os.path.dirname(__file__), "scenarios.json")


# ---------------------------------------------------------------------------
# Agent streaming
# ---------------------------------------------------------------------------

async def stream_chat(
    client: httpx.AsyncClient,
    messages: list[dict],
    token: str,
) -> tuple[str, list[dict]]:
    """Call the agent and return (final_text, tool_calls)."""
    tool_calls: list[dict] = []
    text_parts: list[str] = []
    pending_tool: Optional[dict] = None

    async with client.stream(
        "POST",
        f"{BASE_URL}/api/v1/chat/stream",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"message": messages[-1]["content"]},
        timeout=60.0,
    ) as response:
        if response.status_code != 200:
            body = await response.aread()
            raise RuntimeError(f"HTTP {response.status_code}: {body.decode()}")

        buffer = ""
        async for chunk in response.aiter_text():
            buffer += chunk
            lines = buffer.split("\n\n")
            buffer = lines.pop()
            for line in lines:
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue
                    if data["type"] == "token":
                        text_parts.append(data.get("content", ""))
                    elif data["type"] == "tool_start":
                        pending_tool = {"name": data.get("name", ""), "input": data.get("input", "")}
                    elif data["type"] == "tool_end" and pending_tool:
                        pending_tool["output"] = data.get("output", "")
                        tool_calls.append(pending_tool)
                        pending_tool = None

    return "".join(text_parts), tool_calls


# ---------------------------------------------------------------------------
# Rule-based evaluation (original logic, unchanged)
# ---------------------------------------------------------------------------

def evaluate_scenario(
    scenario: dict,
    final_text: str,
    tool_calls: list[dict],
) -> dict[str, Any]:
    result = {
        "id": scenario["id"],
        "description": scenario["description"],
        "category": scenario["category"],
        "passed": True,
        "checks": [],
        "judge": None,  # filled in later if --judge is enabled
    }

    def check(name: str, ok: bool, detail: str = ""):
        result["checks"].append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            result["passed"] = False

    expected_tool = scenario.get("expected_tool")
    should_escalate = scenario.get("should_escalate", False)
    expected_behavior = scenario.get("expected_behavior", "")

    tool_names_called = [tc["name"] for tc in tool_calls]

    # Check: correct tool called
    if expected_tool:
        tool_ok = expected_tool in tool_names_called
        check(
            "correct_tool_called",
            tool_ok,
            f"Expected '{expected_tool}', got {tool_names_called}",
        )
    else:
        if expected_behavior not in ("ask_for_order_id", "escalate", "refuse_or_redirect"):
            check("no_unexpected_tool", True, "No tool expected and none called")

    # Check: escalation when required
    if should_escalate:
        escalation_keywords = ["escalat", "human agent", "human support", "reach out", "unable to process"]
        escalated = any(kw in final_text.lower() for kw in escalation_keywords)
        check("escalation_triggered", escalated, f"Response: '{final_text[:200]}'")

    # Check: response not empty
    check("response_not_empty", bool(final_text.strip()), "Response was empty")

    # Check: asks for order ID when required
    if expected_behavior == "ask_for_order_id":
        asked = any(
            kw in final_text.lower()
            for kw in ["order id", "order code", "order number", "provide", "share"]
        )
        check("asks_for_order_id", asked, f"Response: '{final_text[:200]}'")

    return result


# ---------------------------------------------------------------------------
# LLM-as-judge
# ---------------------------------------------------------------------------

JUDGE_SYSTEM_PROMPT = """You are an expert evaluator for a customer support AI agent called ShopEase Support.

Your job is to assess the quality of the agent's response to a customer message.
You will be given:
- The customer's message(s)
- What the agent was expected to do (the scenario notes)
- The agent's actual response
- Which tools the agent called (if any)

Score the response on these four dimensions, each from 1 to 5:

1. groundedness (1-5): Does the response only state facts supported by tool results or known policy?
   5 = every claim is traceable to a tool result or clear policy knowledge
   1 = makes up facts, invents numbers or policies not in the tool output

2. accuracy (1-5): Is the response factually correct given the scenario notes?
   5 = fully correct, matches the expected answer
   1 = wrong or contradicts the expected answer

3. helpfulness (1-5): Does the response actually help the customer?
   5 = clear, complete, actionable answer
   1 = vague, unhelpful, or refuses unnecessarily

4. tone (1-5): Is the response warm, professional, and concise?
   5 = excellent customer service tone
   1 = rude, robotic, or excessively long

Return ONLY a valid JSON object with this exact structure, no other text:
{
  "groundedness": <int 1-5>,
  "accuracy": <int 1-5>,
  "helpfulness": <int 1-5>,
  "tone": <int 1-5>,
  "overall": <float, average of the four scores>,
  "reasoning": "<one sentence explaining the main strength or weakness>"
}"""


def _build_judge_prompt(scenario: dict, final_text: str, tool_calls: list[dict]) -> str:
    user_messages = [m["content"] for m in scenario["messages"] if m["role"] == "user"]
    customer_message = " → ".join(user_messages)

    if tool_calls:
        lines = [f"  - {tc['name']}({tc['input']}) → {tc['output'][:200]}" for tc in tool_calls]
        tools_summary = "Tools called:\n" + "\n".join(lines)
    else:
        tools_summary = "Tools called: none"

    return f"""Customer message: "{customer_message}"

Scenario notes (what the agent should do): {scenario.get("notes", "N/A")}
Expected behavior: {scenario.get("expected_behavior", "N/A")}

{tools_summary}

Agent response:
\"\"\"{final_text}\"\"\"

Score this response."""


async def judge_response(
    scenario: dict,
    final_text: str,
    tool_calls: list[dict],
    model: str,
    api_key: str,
) -> dict[str, Any]:
    """Call the LLM judge and return the scoring dict."""
    prompt = _build_judge_prompt(scenario, final_text, tool_calls)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=30.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()

    # Strip markdown fences in case the model wraps its JSON
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()

    scores = json.loads(content)

    # Recompute overall as a safety net
    dims = ["groundedness", "accuracy", "helpfulness", "tone"]
    scores["overall"] = round(sum(scores[d] for d in dims) / len(dims), 2)

    return scores


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def _score_stars(overall: float) -> str:
    if overall >= 4.5:
        return "★★★★★"
    elif overall >= 3.5:
        return "★★★★·"
    elif overall >= 2.5:
        return "★★★··"
    elif overall >= 1.5:
        return "★★···"
    else:
        return "★····"


def print_scenario_result(result: dict, verbose: bool = False) -> None:
    status = "PASS ✓" if result["passed"] else "FAIL ✗"
    judge = result.get("judge")

    judge_str = ""
    if judge and "overall" in judge:
        stars = _score_stars(judge["overall"])
        judge_str = f"  [{stars} {judge['overall']:.1f}/5]"

    print(f"[{result['id']}] {result['description'][:48]:<48} {status}{judge_str}")

    if not result["passed"]:
        for c in result["checks"]:
            if not c["ok"]:
                print(f"    ✗ {c['name']}: {c['detail']}")

    if judge and "overall" in judge and verbose:
        g, a, h, t = judge["groundedness"], judge["accuracy"], judge["helpfulness"], judge["tone"]
        print(f"         groundedness:{g}  accuracy:{a}  helpfulness:{h}  tone:{t}")
        print(f"         Reasoning: {judge['reasoning']}")


def print_summary(results: list[dict], use_judge: bool) -> None:
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    pct = 100 * passed // total if total else 0

    print(f"\n{'='*65}")
    print(f"Rule-based results:  {passed}/{total} passed ({pct}%)")

    by_cat: dict[str, list] = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r["passed"])
    for cat, vals in by_cat.items():
        p, t = sum(vals), len(vals)
        print(f"  {cat}: {p}/{t}")

    if use_judge:
        judged = [r for r in results if r.get("judge") and "overall" in r["judge"]]
        if judged:
            print()
            print(f"LLM-as-judge results:  {len(judged)} scenarios scored  (model: {results[0].get('judge_model', 'gpt-4o-mini')})")
            dims = ["groundedness", "accuracy", "helpfulness", "tone", "overall"]
            for dim in dims:
                avg = sum(r["judge"][dim] for r in judged) / len(judged)
                stars = _score_stars(avg) if dim == "overall" else ""
                label = f"{dim:<14}"
                print(f"  {label}  avg: {avg:.2f}/5  {stars}")

            low = [r for r in judged if r["judge"]["overall"] < 3.0]
            if low:
                print()
                print("  ⚠  Responses scoring below 3.0:")
                for r in low:
                    print(f"    [{r['id']}] {r['description'][:50]}  ({r['judge']['overall']:.1f}/5)")
                    print(f"         → {r['judge']['reasoning']}")

    print(f"{'='*65}\n")


def save_report(results: list[dict], path: str) -> None:
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total": len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "scenarios": results,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved → {path}")


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

async def run_eval(
    token: str,
    category_filter: Optional[str],
    scenario_ids: Optional[list[str]],
    use_judge: bool,
    judge_model: str,
    save_report_path: Optional[str],
    verbose: bool,
) -> None:
    with open(SCENARIOS_FILE) as f:
        scenarios: list[dict] = json.load(f)

    if category_filter:
        scenarios = [s for s in scenarios if s["category"] == category_filter]
    if scenario_ids:
        scenarios = [s for s in scenarios if s["id"] in scenario_ids]

    api_key = os.getenv("OPENAI_API_KEY", "")
    if use_judge and not api_key:
        print("ERROR: --judge requires OPENAI_API_KEY to be set in your environment.")
        sys.exit(1)

    print(f"\n{'='*65}")
    mode = "rule-based + LLM-as-judge" if use_judge else "rule-based only"
    print(f"ShopEase Agent Evaluation  [{mode}]  —  {len(scenarios)} scenario(s)")
    print(f"{'='*65}\n")

    results = []
    async with httpx.AsyncClient() as client:
        for scenario in scenarios:
            sys.stdout.write(f"Running [{scenario['id']}] ... ")
            sys.stdout.flush()

            try:
                final_text, tool_calls = await stream_chat(client, scenario["messages"], token)
                result = evaluate_scenario(scenario, final_text, tool_calls)
                result["response"] = final_text
                result["tool_calls"] = tool_calls

                if use_judge:
                    try:
                        scores = await judge_response(
                            scenario, final_text, tool_calls, judge_model, api_key
                        )
                        scores["judge_model"] = judge_model
                        result["judge"] = scores
                        result["judge_model"] = judge_model
                    except Exception as exc:
                        result["judge"] = {"error": str(exc)}

                print_scenario_result(result, verbose=verbose)
                results.append(result)

            except Exception as exc:
                print(f"ERROR: {exc}")
                results.append({
                    "id": scenario["id"],
                    "description": scenario["description"],
                    "category": scenario["category"],
                    "passed": False,
                    "checks": [{"name": "run", "ok": False, "detail": str(exc)}],
                    "judge": None,
                })

    print_summary(results, use_judge)

    if save_report_path:
        save_report(results, save_report_path)

    if sum(1 for r in results if r["passed"]) < len(results):
        sys.exit(1)


def main():
    global BASE_URL
    parser = argparse.ArgumentParser(description="Evaluate the ShopEase support agent")
    parser.add_argument("--api-url", default=BASE_URL)
    parser.add_argument("--token", required=True, help="JWT auth token")
    parser.add_argument("--category", choices=["policy", "order", "escalation"])
    parser.add_argument("--ids", nargs="*", help="Specific scenario IDs to run")
    parser.add_argument("--judge", action="store_true", help="Enable LLM-as-judge scoring")
    parser.add_argument("--judge-model", default="gpt-4o-mini")
    parser.add_argument("--report", action="store_true", help="Save JSON report to tests/eval_report.json")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-scenario judge reasoning")
    args = parser.parse_args()

    BASE_URL = args.api_url

    report_path = (
        os.path.join(os.path.dirname(__file__), "eval_report.json") if args.report else None
    )

    asyncio.run(run_eval(
        token=args.token,
        category_filter=args.category,
        scenario_ids=args.ids,
        use_judge=args.judge,
        judge_model=args.judge_model,
        save_report_path=report_path,
        verbose=args.verbose,
    ))


if __name__ == "__main__":
    main()