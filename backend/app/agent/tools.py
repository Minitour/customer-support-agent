"""Build user-scoped LangChain tools for a single request."""
from typing import Optional

from langchain_core.tools import tool

from app.vectorstore.ingestion import get_policy_vectorstore


def build_tools(user_id: Optional[int] = None, order_repo=None):
    """
    Returns a list of LangChain tools.

    When ``user_id`` and ``order_repo`` are provided (authenticated user), the
    order-lookup tool is included. For guests (no user), only the policy search
    tool is exposed so the agent can answer policy-related questions only.
    """

    @tool
    async def search_policy(query: str) -> str:
        """Search the ShopEase policy knowledge base for information about returns, shipping, payments, warranties, and contact information."""
        vs = get_policy_vectorstore()
        docs = vs.similarity_search(query, k=3)
        if not docs:
            return "No relevant policy information found."
        return "\n\n---\n\n".join(d.page_content for d in docs)

    if user_id is None or order_repo is None:
        return [search_policy]

    @tool
    async def get_order_status(order_id: str) -> str:
        """Look up an order by its order code (e.g. 'A12345'). Only works for orders belonging to the current customer."""
        order = await order_repo.get_by_code(order_id.strip().upper(), user_id=user_id)
        if order is None:
            return f"No order with code '{order_id}' found for your account."
        eta_str = order.eta.strftime("%B %d, %Y") if order.eta else "unknown"
        return (
            f"Order {order.order_code}: status={order.status.value}, "
            f"carrier={order.carrier}, tracking={order.tracking}, ETA={eta_str}."
        )

    return [search_policy, get_order_status]
