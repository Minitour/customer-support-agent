#!/usr/bin/env python3
"""
Evaluation harness for the ShopEase customer support agent.

Usage:
    python tests/eval.py --token <jwt> [options]

Options:
    --category policy|order|escalation   Filter by scenario category
    --ids T01 T02 ...                    Run specific scenario IDs
    --judge                              Enable LLM-as-judge scoring (requires OPENAI_API_KEY)
    --judge-model gpt-4o-mini            Single judge model
    --judge-models m1 m2 ...             Several judge models to compare
    --report                             Save a JSON report to tests/eval_report.json
    --verbose / -v                       Show judge reasoning per scenario
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


async def stream_chat(client, messages, token):
    """Call the agent and return (final_text, tool_calls)."""
    tool_calls = []
    text_parts = []
    pending_tool = None

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


def evaluate_scenario(scenario, final_text, tool_calls):
    result = {
        "id": scenario["id"],
        "description": scenario["description"],
        "category": scenario["category"],
        "passed": True,
        "checks": [],
        "judge": None,
    }

    def check(name, ok, detail=""):
        result["checks"].append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            result["passed"] = False

    expected_tool = scenario.get("expected_tool")
    expected_tools = scenario.get("expected_tools")
    expected_behavior = scenario.get("expected_behavior", "")

    tool_names_called = [tc["name"] for tc in tool_calls]

    required_tools = []
    if expected_tools:
        required_tools = expected_tools
    elif expected_tool:
        required_tools = [expected_tool]

    if required_tools:
        missing = [t for t in required_tools if t not in tool_names_called]
        check(
            "correct_tools_called",
            not missing,
            f"Expected {required_tools}, got {tool_names_called}"
            + (f" (missing {missing})" if missing else ""),
        )
    else:
        if expected_behavior not in ("ask_for_order_id", "escalate", "refuse_or_redirect"):
            check("no_unexpected_tool", True, "No tool expected and none called")

    check("response_not_empty", bool(final_text.strip()), "Response was empty")

    if expected_behavior == "ask_for_order_id":
        asked = any(
            kw in final_text.lower()
            for kw in ["order id", "order code", "order number", "provide", "share"]
        )
        check("asks_for_order_id", asked, f"Response: '{final_text[:200]}'")

    return result


JUDGE_SYSTEM_PROMPT = """You are an expert evaluator for a customer support AI agent called ShopEase Support.

Your job is to assess the quality of the agent's response to a customer message.
You will be given:
- The customer's message(s)
- What the agent was expected to do (the scenario notes)
- The agent's actual response
- Which tools the agent called (if any)

Score the response on these four dimensions, each from 1 to 5:

1. groundedness (1-5): Does the response only state facts supported by tool results or known policy?
2. accuracy (1-5): Is the response factually correct given the scenario notes?
3. helpfulness (1-5): Does the response actually help the customer?
4. tone (1-5): Is the response warm, professional, and concise?

Return ONLY a valid JSON object with this exact structure, no other text:
{
  "groundedness": <int 1-5>,
  "accuracy": <int 1-5>,
  "helpfulness": <int 1-5>,
  "tone": <int 1-5>,
  "overall": <float, average of the four scores>,
  "reasoning": "<one sentence explaining the main strength or weakness>"
}"""


def _build_judge_prompt(scenario, final_text, tool_calls):
    user_messages = [m["content"] for m in scenario["messages"] if m["role"] == "user"]
    customer_message = " -> ".join(user_messages)

    if tool_calls:
        lines = [f"  - {tc['name']}({tc['input']}) -> {tc['output'][:200]}" for tc in tool_calls]
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


async def judge_response(scenario, final_text, tool_calls, model, api_key):
    """Call one LLM judge and return the scoring dict."""
    prompt = _build_judge_prompt(scenario, final_text, tool_calls)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    # Reasoning models (o1/o3 family) reject the temperature parameter.
    if not model.startswith(("o1", "o3")):
        payload["temperature"] = 0

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()

    scores = json.loads(content)
    dims = ["groundedness", "accuracy", "helpfulness", "tone"]
    scores["overall"] = round(sum(scores[d] for d in dims) / len(dims), 2)
    return scores


def _score_stars(overall):
    if overall >= 4.5:
        return "*****"
    elif overall >= 3.5:
        return "****."
    elif overall >= 2.5:
        return "***.."
    elif overall >= 1.5:
        return "**..."
    return "*...."


def print_scenario_result(result, verbose=False):
    status = "PASS" if result["passed"] else "FAIL"
    judge = result.get("judge")
    judge_str = ""
    if judge and "overall" in judge:
        judge_str = f"  [{_score_stars(judge['overall'])} {judge['overall']:.1f}/5]"
    print(f"[{result['id']}] {result['description'][:48]:<48} {status}{judge_str}")
    if not result["passed"]:
        for c in result["checks"]:
            if not c["ok"]:
                print(f"    x {c['name']}: {c['detail']}")
    if judge and "overall" in judge and verbose:
        g, a, h, t = judge["groundedness"], judge["accuracy"], judge["helpfulness"], judge["tone"]
        print(f"         groundedness:{g}  accuracy:{a}  helpfulness:{h}  tone:{t}")
        print(f"         Reasoning: {judge['reasoning']}")


def print_summary(results, use_judge):
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    pct = 100 * passed // total if total else 0
    print(f"\n{'='*65}")
    print(f"Rule-based results:  {passed}/{total} passed ({pct}%)")
    by_cat = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r["passed"])
    for cat, vals in by_cat.items():
        print(f"  {cat}: {sum(vals)}/{len(vals)}")
    print(f"{'='*65}\n")


def save_report(results, path):
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total": len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "scenarios": results,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved -> {path}")


def _tool_type(scenario):
    expected_tools = scenario.get("expected_tools")
    expected_tool = scenario.get("expected_tool")
    if expected_tools:
        return "multiple" if len(expected_tools) > 1 else "single"
    if expected_tool:
        return "single"
    return "none"


def save_result(records, path):
    total = len(records)
    passed = sum(1 for r in records if r.get("passed"))
    failed = total - passed

    dims = ["groundedness", "accuracy", "helpfulness", "tone", "overall"]
    model_names = []
    for r in records:
        for m in r.get("judges", {}):
            if m not in model_names:
                model_names.append(m)

    judge_models_summary = {}
    for m in model_names:
        agg = {d: [] for d in dims}
        for r in records:
            s = r.get("judges", {}).get(m, {})
            for d in dims:
                if isinstance(s.get(d), (int, float)):
                    agg[d].append(s[d])
        judge_models_summary[m] = {
            d: round(sum(v) / len(v), 2) if v else None for d, v in agg.items()
        }

    by_tool_type = {}
    for r in records:
        tt = r.get("tool_type", "none")
        by_tool_type.setdefault(tt, {"passed": 0, "total": 0})
        by_tool_type[tt]["total"] += 1
        if r.get("passed"):
            by_tool_type[tt]["passed"] += 1

    output = {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(100 * passed // total) if total else 0}%",
            "by_tool_type": by_tool_type,
            "judge_models": judge_models_summary,
        },
        "results": records,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"result.json written -> {path}")


async def run_eval(token, category_filter, scenario_ids, use_judge, judge_models, save_report_path, verbose):
    with open(SCENARIOS_FILE) as f:
        scenarios = json.load(f)

    if category_filter:
        scenarios = [s for s in scenarios if s["category"] == category_filter]
    if scenario_ids:
        scenarios = [s for s in scenarios if s["id"] in scenario_ids]

    api_key = os.getenv("OPENAI_API_KEY", "")
    if use_judge and not api_key:
        print("ERROR: --judge requires OPENAI_API_KEY to be set in your environment.")
        sys.exit(1)

    print(f"\n{'='*65}")
    mode = f"rule-based + LLM-as-judge ({', '.join(judge_models)})" if use_judge else "rule-based only"
    print(f"ShopEase Agent Evaluation  [{mode}]  -  {len(scenarios)} scenario(s)")
    print(f"{'='*65}\n")

    results = []
    output_records = []
    async with httpx.AsyncClient() as client:
        for scenario in scenarios:
            sys.stdout.write(f"Running [{scenario['id']}] ... ")
            sys.stdout.flush()

            try:
                final_text, tool_calls = await stream_chat(client, scenario["messages"], token)
                result = evaluate_scenario(scenario, final_text, tool_calls)
                result["response"] = final_text
                result["tool_calls"] = tool_calls

                judges = {}
                if use_judge:
                    for jm in judge_models:
                        try:
                            judges[jm] = await judge_response(scenario, final_text, tool_calls, jm, api_key)
                        except Exception as exc:
                            judges[jm] = {"error": str(exc)}
                    primary = judges.get(judge_models[0], {})
                    if "overall" in primary:
                        result["judge"] = primary
                        result["judge_model"] = judge_models[0]

                print_scenario_result(result, verbose=verbose)
                results.append(result)

                output_records.append({
                    "id": f"R{len(output_records) + 1:02d}",
                    "scenario": scenario["id"],
                    "category": scenario.get("category", "other"),
                    "query": next((m["content"] for m in reversed(scenario["messages"]) if m["role"] == "user"), ""),
                    "expected_tool": scenario.get("expected_tools") or scenario.get("expected_tool"),
                    "tool_type": _tool_type(scenario),
                    "calling_tools": [tc["name"] for tc in tool_calls],
                    "final_answer": final_text,
                    "passed": result["passed"],
                    "judges": judges,
                })

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
                output_records.append({
                    "id": f"R{len(output_records) + 1:02d}",
                    "scenario": scenario["id"],
                    "category": scenario.get("category", "other"),
                    "query": next((m["content"] for m in reversed(scenario["messages"]) if m["role"] == "user"), ""),
                    "expected_tool": scenario.get("expected_tools") or scenario.get("expected_tool"),
                    "tool_type": _tool_type(scenario),
                    "calling_tools": [],
                    "final_answer": f"ERROR: {exc}",
                    "passed": False,
                    "judges": {},
                })

    print_summary(results, use_judge)
    save_result(output_records, os.path.join(os.path.dirname(__file__), "result.json"))

    if save_report_path:
        save_report(results, save_report_path)


def main():
    global BASE_URL
    parser = argparse.ArgumentParser(description="Evaluate the ShopEase support agent")
    parser.add_argument("--api-url", default=BASE_URL)
    parser.add_argument("--token", required=True, help="JWT auth token")
    parser.add_argument("--category", choices=["policy", "order", "escalation"])
    parser.add_argument("--ids", nargs="*", help="Specific scenario IDs to run")
    parser.add_argument("--judge", action="store_true", help="Enable LLM-as-judge scoring")
    parser.add_argument("--judge-model", default="gpt-4o-mini", help="Single judge model")
    parser.add_argument("--judge-models", nargs="*",
                        help="Several judge models to compare, e.g. o3-mini o1-mini gpt-4o gpt-4o-mini")
    parser.add_argument("--report", action="store_true", help="Save JSON report to tests/eval_report.json")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-scenario judge reasoning")
    args = parser.parse_args()

    BASE_URL = args.api_url
    judge_models = args.judge_models if args.judge_models else [args.judge_model]

    report_path = (
        os.path.join(os.path.dirname(__file__), "eval_report.json") if args.report else None
    )

    asyncio.run(run_eval(
        token=args.token,
        category_filter=args.category,
        scenario_ids=args.ids,
        use_judge=args.judge,
        judge_models=judge_models,
        save_report_path=report_path,
        verbose=args.verbose,
    ))


if __name__ == "__main__":
    main()
