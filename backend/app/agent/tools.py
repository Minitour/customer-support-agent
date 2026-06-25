"""Build user-scoped LangChain tools for a single request."""
from typing import Optional
import json

from langchain_core.tools import tool

from app.vectorstore.ingestion import get_policy_vectorstore, get_products_vectorstore


def build_tools(user_id: Optional[int] = None, order_repo=None, product_repo=None, user_repo=None):
    """
    Returns a list of LangChain tools.

    When ``user_id`` and ``order_repo`` are provided (authenticated user), the
    order-lookup tools are included. For guests (no user), only the policy and
    product search/lookup tools are exposed.
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

    @tool
    async def get_products_by_id(ids: list[int]) -> str:
        """Look up one or more products by their numeric product IDs. Use this to get
        the title, category, brand, price, and stock for products the customer is
        currently viewing on screen or has in their cart (their IDs are provided in
        the page context). Pass a list of product IDs, e.g. [3, 7, 12]."""
        if product_repo is None:
            return "Product lookup is unavailable right now."
        products = await product_repo.get_by_ids(ids)
        if not products:
            return "No products found for the given IDs."
        by_id = {p.id: p for p in products}
        lines = []
        for pid in ids:
            p = by_id.get(pid)
            if p is None:
                lines.append(f"- ID {pid}: not found")
                continue
            try:
                price = f"${float(p.price):.2f}"
            except (ValueError, TypeError):
                price = "N/A"
            link = f"[{p.title}](/products/{p.id})"
            lines.append(
                f"- {link} (ID: {p.id}) | Category: {p.category or 'N/A'} "
                f"| Brand: {p.brand or 'N/A'} | Price: {price} | Stock: {p.stock}"
            )
        return "\n".join(lines)
    
    @tool
    async def escalate_to_human(name: str, email: str, reason: str) -> str:
        """Escalate to a human agent for any request you can't handle (e.g. changing
            a password, account changes) or when the customer asks for a human.
            Ask the customer for their name and email first, then call this."""
        return f"Ticket created for {name}. A human agent will email you at {email} shortly."


    base_tools = [search_policy, search_products, get_products_by_id, escalate_to_human]

    if user_id is None or order_repo is None:
        return base_tools

    @tool
    async def get_order_status(order_id: str) -> str:
        """Look up an order by its order code (e.g. 'A12345'). Only works for orders belonging to the current customer."""
        order = await order_repo.get_by_code(order_id.strip().upper(), user_id=user_id)
        if order is None:
            return f"No order with code '{order_id}' found for your account."
        eta_str = order.eta.strftime("%B %d, %Y") if order.eta else "unknown"
        delivered_str = (
            order.delivered_at.strftime("%B %d, %Y at %I:%M %p") if order.delivered_at else None
        )
        details = (
            f"Order {order.order_code}: status={order.status.value}, "
            f"carrier={order.carrier}, tracking={order.tracking}, ETA={eta_str}"
        )
        if delivered_str:
            details += f", delivered on {delivered_str}"
        return details + "."

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
            delivered_str = (
                order.delivered_at.strftime("%B %d, %Y at %I:%M %p")
                if order.delivered_at
                else None
            )
            line = (
                f"• {order.order_code} — placed {date_str}, "
                f"status: {order.status.value}, "
                f"{item_count} item(s), total: ${order.total:.2f}, ETA: {eta_str}"
            )
            if delivered_str:
                line += f", delivered on {delivered_str}"
            lines.append(line + ".")
        return "\n".join(lines)
    
    if escalate_to_human in base_tools:
        base_tools.remove(escalate_to_human)
    
    @tool
    async def escalate_to_human(reason: str, order_id: Optional[str] = None) -> str:
        """Escalate a request to a human support agent. Use for actions you can't perform
        (cancel/modify/return an order) or when the customer asks for a human.
        For order-related actions, include the order_id; ask for it first if missing.

        Returns the escalation result as data. If status is "order_not_found", tell the
        customer no order with that ID exists on their account. If status is "escalated",
        confirm the escalation and show them the submitted_message so they see what was sent."""
        
        if order_id is not None:
            order = await order_repo.get_by_code(order_id.strip().upper(), user_id=user_id)
            if order is None:
                return json.dumps({"status": "order_not_found", "order_id": order_id})

        user = await user_repo.get_by_id(user_id)

        submitted_message = (
            f"Customer: {user.name} ({user.email}) | "
            f"Order: {order_id or 'N/A'} | Reason: {reason}"
        )

        return json.dumps({
            "status": "escalated",
            "customer_email": user.email,
            "submitted_message": submitted_message,
        })
    
    return base_tools + [get_order_status, get_order_history, escalate_to_human]
