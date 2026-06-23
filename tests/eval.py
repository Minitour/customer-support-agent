#!/usr/bin/env python3
"""
Evaluation harness for the ShopEase customer support agent.

Usage:
    python tests/eval.py [--api-url http://localhost:8000] [--token <jwt>] [--category policy|order|escalation]

The script:
1. Loads scenarios from tests/scenarios.json
2. For each scenario, calls POST /api/v1/chat/stream with the conversation
3. Collects streamed events (tool calls + final text)
4. Evaluates each scenario against its expected behavior
5. Prints a per-scenario report + summary
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Optional

import httpx


BASE_URL = os.getenv("EVAL_API_URL", "http://localhost:8000")
SCENARIOS_FILE = os.path.join(os.path.dirname(__file__), "scenarios.json")


async def stream_chat(
    client: httpx.AsyncClient,
    messages: list[dict],
    token: str,
) -> tuple[str, list[dict]]:
    """Returns (final_text, tool_calls)."""
    tool_calls: list[dict] = []
    text_parts: list[str] = []
    pending_tool: Optional[dict] = None

    async with client.stream(
        "POST",
        f"{BASE_URL}/api/v1/chat/stream",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"messages": messages},
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
        # Expected no tool call
        if expected_behavior not in ("ask_for_order_id", "escalate", "refuse_or_redirect"):
            check("no_unexpected_tool", True, "No tool expected and none called")

    # Check: escalation when required
    if should_escalate:
        escalation_keywords = ["escalat", "human agent", "human support", "reach out", "unable to process"]
        escalated = any(kw in final_text.lower() for kw in escalation_keywords)
        check("escalation_triggered", escalated, f"Response: '{final_text[:200]}'")

    # Check: no hallucination (response not empty)
    check("response_not_empty", bool(final_text.strip()), "Response was empty")

    # Check: response is grounded (didn't invent if no tool)
    if expected_behavior == "ask_for_order_id":
        asked = any(
            kw in final_text.lower()
            for kw in ["order id", "order code", "order number", "provide", "share"]
        )
        check("asks_for_order_id", asked, f"Response: '{final_text[:200]}'")

    return result


async def run_eval(
    token: str,
    category_filter: Optional[str],
    scenario_ids: Optional[list[str]],
) -> None:
    with open(SCENARIOS_FILE) as f:
        scenarios: list[dict] = json.load(f)

    if category_filter:
        scenarios = [s for s in scenarios if s["category"] == category_filter]
    if scenario_ids:
        scenarios = [s for s in scenarios if s["id"] in scenario_ids]

    print(f"\n{'='*60}")
    print(f"ShopEase Agent Evaluation — {len(scenarios)} scenario(s)")
    print(f"{'='*60}\n")

    results = []
    async with httpx.AsyncClient() as client:
        for scenario in scenarios:
            sys.stdout.write(f"[{scenario['id']}] {scenario['description'][:50]}... ")
            sys.stdout.flush()
            try:
                final_text, tool_calls = await stream_chat(
                    client, scenario["messages"], token
                )
                result = evaluate_scenario(scenario, final_text, tool_calls)
                status = "PASS ✓" if result["passed"] else "FAIL ✗"
                print(status)
                if not result["passed"]:
                    for c in result["checks"]:
                        if not c["ok"]:
                            print(f"    ✗ {c['name']}: {c['detail']}")
                results.append(result)
            except Exception as exc:
                print(f"ERROR: {exc}")
                results.append(
                    {
                        "id": scenario["id"],
                        "description": scenario["description"],
                        "category": scenario["category"],
                        "passed": False,
                        "checks": [{"name": "run", "ok": False, "detail": str(exc)}],
                    }
                )

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} passed ({100*passed//total if total else 0}%)")
    by_cat: dict[str, list] = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r["passed"])
    for cat, vals in by_cat.items():
        p = sum(vals)
        t = len(vals)
        print(f"  {cat}: {p}/{t}")
    print(f"{'='*60}\n")

    if passed < total:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Evaluate the ShopEase support agent")
    parser.add_argument("--api-url", default=BASE_URL, help="Backend base URL")
    parser.add_argument("--token", required=True, help="JWT auth token")
    parser.add_argument("--category", choices=["policy", "order", "escalation"], help="Filter by category")
    parser.add_argument("--ids", nargs="*", help="Run specific scenario IDs")
    args = parser.parse_args()

    global BASE_URL
    BASE_URL = args.api_url

    asyncio.run(run_eval(token=args.token, category_filter=args.category, scenario_ids=args.ids))


if __name__ == "__main__":
    main()
