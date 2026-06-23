"""Build user-scoped LangChain tools for a single request."""
from typing import Optional

from langchain_core.tools import tool

from app.vectorstore.ingestion import get_policy_vectorstore, get_products_vectorstore


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

    @tool
    async def search_products(query: str) -> str:
        """Search the product catalog using natural language. Use this when a customer asks about specific products, categories, brands, or wants product recommendations. Returns the top matching products with their ID, title, category, brand, and price."""
        vs = get_products_vectorstore()
        docs = vs.similarity_search(query, k=5)
        if not docs:
            return "No matching products found in the catalog."
        lines = []
        for doc in docs:
            m = doc.metadata
            title = doc.page_content.splitlines()[0]
            price = m.get("price", "N/A")
            try:
                price = f"${float(price):.2f}"
            except (ValueError, TypeError):
                price = "N/A"
            product_id = m.get("product_id", "")
            link = f"[{title}](/products/{product_id})" if product_id else title
            lines.append(
                f"- {link} "
                f"| Category: {m.get('category', 'N/A')} "
                f"| Brand: {m.get('brand', 'N/A')} "
                f"| Price: {price}"
            )
        return "\n".join(lines)

    if user_id is None or order_repo is None:
        return [search_policy, search_products]

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

    @tool
    async def get_order_history() -> str:
        """Return a summary of all orders placed by the current customer, sorted most-recent first."""
        orders = await order_repo.list_for_user(user_id)
        if not orders:
            return "You have no orders yet."
        lines = []
        for order in orders:
            eta_str = order.eta.strftime("%B %d, %Y") if order.eta else "unknown"
            date_str = order.created_at.strftime("%B %d, %Y")
            item_count = sum(i.quantity for i in order.items)
            lines.append(
                f"• {order.order_code} — placed {date_str}, "
                f"status: {order.status.value}, "
                f"{item_count} item(s), total: ${order.total:.2f}, ETA: {eta_str}."
            )
        return "\n".join(lines)

    return [search_policy, search_products, get_order_status, get_order_history]
