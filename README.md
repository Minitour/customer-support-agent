# ShopEase Customer Support Agent

A full-stack fictional online store with an AI-powered customer support agent. The agent answers policy questions from a knowledge base, looks up order status, and escalates to a human when it cannot help.

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite + Tailwind CSS + shadcn-style components |
| Backend | FastAPI (Python 3.12) + async SQLAlchemy |
| Database | PostgreSQL 16 |
| Vector Store | ChromaDB 0.6 |
| LLM / Agent | LangChain + LangGraph + OpenAI (gpt-4o-mini) |
| Embeddings | OpenAI text-embedding-3-small |
| Container | Docker Compose |

## Features

- **Auth** — Sign up / sign in with JWT long-lived sessions
- **Product Catalog** — Browse 194 products, filter by category, search
- **Cart & Checkout** — Add to cart, checkout → creates an order
- **Orders** — View order list, detail page, cancel orders
- **Auto-promotion** — Background job advances each order one stage (`created` → `received` → `processing` → `shipped` → `delivered`) every 30 seconds
- **Support Chat** — Streamed AI responses with a collapsible tool-call side panel

## Agent Tools

### `search_policy(query: str) → str`
Searches the policy knowledge base using semantic similarity. Returns the top-3 most relevant policy chunks.

**Covers:** return policy, shipping zones & costs, payment methods, warranty, cancellation/refunds, privacy, contact info.

### `get_order_status(order_id: str) → str`
Looks up a specific order by its order code (e.g. `A12345`). Returns status, carrier, tracking number, and ETA.

**User-scoped:** Only returns orders belonging to the authenticated user. Attempts to look up another user's order return "not found."

## Escalation Policy

The agent can only provide information — it never performs actions. Any action request is handed off to a human via the `escalate_to_human` tool.

**Signed-in customers:** name and email are pulled from the database automatically. For order actions, the agent includes the order ID, and the tool checks it exists and belongs to the customer before escalating.
- *"Please cancel order A12345"* → verifies the order, then escalates.

**Guests:** the agent asks for name and email first, then escalates.
- *"I'd like to change my password"* → asks for name + email, then escalates.

**Never invents** information — only answers with what tool results contain.

## Policy Knowledge Base

Located in `.data/policy/`:

| File | Coverage |
|------|----------|
| `01_return_policy.md` | 30-day returns, sale items → store credit, non-returnable items |
| `02_shipping.md` | Shipping zones, carriers, free shipping threshold, tracking |
| `03_payments.md` | Credit/debit cards, digital wallets, BNPL, security |
| `04_warranty.md` | Manufacturer warranty by category, claim process |
| `05_cancellations_and_refunds.md` | Order cancellation eligibility, refund timelines |
| `06_privacy_and_data.md` | Data collection, retention, user rights |
| `07_contact_and_escalation.md` | Support channels, hours, escalation triggers |

## Quickstart

### Prerequisites

- Docker + Docker Compose
- An OpenAI API key

### 1. Clone and configure

```bash
git clone <repo-url>
cd customer-support-agent
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

### 2. Start all services

```bash
docker compose up --build
```

First boot automatically:
- Creates PostgreSQL tables
- Seeds 194 products from `.data/products.json`
- Embeds and indexes policy documents into ChromaDB
- Embeds product catalog into ChromaDB

Access the app at **http://localhost:3000** (or frontend direct at **http://localhost:5173** if running locally).

### 3. Run locally (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
# Set env vars (DATABASE_URL, OPENAI_API_KEY, CHROMA_HOST, etc.)
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

### 4. Setup development agent harness - skills for Cursor/Claude/etc
Install [capa](https://capa.infragate.ai) and run
```bash
capa install
```

## Running the Evaluation

First, obtain a JWT token by signing up:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"TESTtest","name":"Eval User"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

python tests/eval.py --token "$TOKEN"
```

Filter by category:
```bash
python tests/eval.py --token "$TOKEN" --category policy
python tests/eval.py --token "$TOKEN" --category order
python tests/eval.py --token "$TOKEN" --category escalation
```

Run specific scenarios:
```bash
python tests/eval.py --token "$TOKEN" --ids P01 P02 E01
```
## QA and Evaluation

In addition to the automated evaluation scenarios in `tests/`, this project includes a manual QA checklist for validating the AI customer support agent.

The QA checklist covers:
- return policy questions
- sale item refund rules
- damaged item handling
- non-returnable items
- refund timing
- hallucination checks
- privacy checks for order-related questions

See [QA_CHECKLIST.md](QA_CHECKLIST.md) for detailed manual test cases.

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Create account → returns JWT |
| POST | `/api/v1/auth/signin` | Sign in → returns JWT |
| GET | `/api/v1/auth/me` | Current user info |
| GET | `/api/v1/products` | List products (category, search, pagination) |
| GET | `/api/v1/products/categories` | Available categories |
| GET | `/api/v1/products/{id}` | Product detail |
| POST | `/api/v1/orders` | Checkout (requires auth) |
| GET | `/api/v1/orders` | User's orders (requires auth) |
| GET | `/api/v1/orders/{id}` | Order detail (requires auth) |
| POST | `/api/v1/orders/{id}/cancel` | Cancel order (requires auth) |
| POST | `/api/v1/chat/stream` | SSE streaming chat (requires auth) |
| GET | `/health` | Health check |

Interactive docs: **http://localhost:8000/docs**

## Project Structure

```
customer-support-agent/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangChain agent, tools, system prompt
│   │   ├── api/routes/     # FastAPI route handlers
│   │   ├── core/           # Config, security (JWT/bcrypt)
│   │   ├── db/             # Async SQLAlchemy engine/session
│   │   ├── jobs/           # Auto-delivery background job
│   │   ├── models/         # SQLAlchemy models
│   │   ├── repositories/   # Repository pattern data access
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── vectorstore/    # Chroma client + ingestion helpers
│   │   └── main.py         # App entry + lifespan
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/     # UI components, layout, cart drawer
│       ├── lib/            # API client, utilities
│       ├── pages/          # Catalog, Orders, Chat, Auth
│       └── store/          # Zustand (auth, cart)
├── .data/
│   ├── products.json       # 194 products (seed data)
│   └── policy/             # 7 policy markdown files
├── tests/
│   ├── scenarios.json      # 30 evaluation scenarios
│   └── eval.py             # Eval harness
├── docker-compose.yml
└── .env.example
```
