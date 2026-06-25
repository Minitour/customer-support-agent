"""LangChain agent with streaming support (OpenAI or Ollama)."""
from typing import AsyncGenerator, Optional

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from app.core.config import settings
from app.agent.prompt import SYSTEM_PROMPT, GUEST_SYSTEM_PROMPT, GUARDRAILS
from app.agent.tools import build_tools


def _build_llm():
    provider = settings.LLM_PROVIDER.lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.1,
            streaming=True,
            api_key=settings.OPENAI_API_KEY,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            temperature=0.1,
            base_url=settings.OLLAMA_BASE_URL,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER!r}. "
        "Expected 'openai' or 'ollama'."
    )


def _build_agent(tools, prompt: str):
    llm = _build_llm()
    return create_react_agent(llm, tools, prompt=prompt)


def _convert_messages(messages: list[dict], context_text: Optional[str] = None) -> list:
    """Convert DB message dicts to LangChain message objects.

    The context_text (current page context) is merged into the FINAL user message
    rather than added as a separate system message. ``create_react_agent`` already
    injects the system prompt as the single leading system message, and chat
    templates (e.g. Ollama/qwen) only honor that leading system slot — a second
    system message mid-conversation is silently ignored. Folding the context into
    the user's own turn guarantees the model reads it. The context is never
    persisted, and since the latest user message is new every turn anyway, the
    persisted history remains a stable, cacheable prefix.
    """
    converted = []
    for m in messages:
        role = m["role"]
        content = m["content"]
        if role == "user":
            converted.append(HumanMessage(content=content))
        elif role == "assistant":
            converted.append(AIMessage(content=content))

    if context_text:
        if converted and isinstance(converted[-1], HumanMessage):
            merged = f"{converted[-1].content}\n\n{context_text}"
            converted[-1] = HumanMessage(content=merged)
        else:
            converted.append(HumanMessage(content=context_text))
    return converted


async def stream_agent_response(
    user_id: Optional[int],
    order_repo,
    user_repo,
    messages: list[dict],
    product_repo=None,
    context_text: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Streams SSE-compatible events.
    Yields strings in the format:
      data: <json>\\n\\n
    where json has one of:
      {"type": "token", "content": "..."}
      {"type": "tool_start", "name": "...", "input": "..."}
      {"type": "tool_end", "name": "...", "output": "..."}
      {"type": "done"}
    """
    import json

    is_guest = user_id is None
    tools = build_tools(user_id, order_repo, product_repo, user_repo)
    base_prompt = GUEST_SYSTEM_PROMPT if is_guest else SYSTEM_PROMPT
    # Keep the system prompt stable (cacheable prefix); context is appended as a
    # trailing message in _convert_messages, never concatenated into the prompt.
    prompt = f"{base_prompt}\n\n{GUARDRAILS}"
    agent = _build_agent(tools, prompt)
    converted = _convert_messages(messages, context_text=context_text)

    async for event in agent.astream_events({"messages": converted}, version="v2"):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            chunk = event["data"].get("chunk")
            if chunk and chunk.content:
                yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

        elif kind == "on_tool_start":
            name = event.get("name", "")
            inp = event["data"].get("input", {})
            yield f"data: {json.dumps({'type': 'tool_start', 'name': name, 'input': str(inp)})}\n\n"

        elif kind == "on_tool_end":
            name = event.get("name", "")
            out = event["data"].get("output", "")
            yield f"data: {json.dumps({'type': 'tool_end', 'name': name, 'output': str(out)})}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
