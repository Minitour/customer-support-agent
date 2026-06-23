# Customer Support Agent

Note. This page lays out one full version of the project — the goal, a sample input/output, suggested tools, and a step-by-step plan. Treat it as a reference, not a script. Your team can pick a different angle, swap libraries, narrow the scope, or take the project somewhere we did not anticipate. As long as the final deliverable makes sense for the goal, you are on track.
Task. Build a customer-support agent for an imaginary product (a software tool, an online shop, an airline — pick something concrete). The agent should answer common questions from a knowledge base, handle multi-turn clarifications, look up order or account information using a simple tool, and escalate to a human when uncertain. Write 30 test conversations covering FAQ-style questions, account lookups, and tricky cases that should escalate. You could use any LLM, any vector store for the knowledge base (FAISS, Chroma), a small SQLite "orders" table for the lookup tool, and any agent framework (LangChain, smolagents, or pure Python). Going further (optional). Build a Streamlit chat UI with a side panel showing the agent's reasoning and tool calls, or add a sentiment classifier that detects frustrated customers and escalates earlier.
Resources: CPU works with a hosted LLM; Colab T4 / 8GB GPU if you run a local open model.
What you'll build
Build a customer-support agent for a fictional online store. The agent must (1) answer policy questions from a knowledge base (return policy, shipping zones, payment methods), (2) look up order status by order ID via a function-call to a fake order API, and (3) escalate when it does not know — without making things up. The team builds the tool definitions, the prompt that routes between knowledge-base lookup and function-call, and a small evaluation harness with realistic test scenarios.

What goes in, what comes out
Input
A user message from a chat textbox. Optionally an order ID, shipping address, or product reference.

Output
A response that may be a direct answer, an order-status lookup result, or a "I cannot help — escalating to a human" message. Plus a transcript of which tool was called and why.

User messages and expected routing
Message 1: "What is your return policy for items bought on sale?"
  Expected: retrieve from policy KB → answer.

Message 2: "Where is my order? Order ID is A-12489."
  Expected: call get_order_status("A-12489") → format the result.

Message 3: "Can you cancel my subscription and refund last month?"
  Expected: agent does NOT have a cancel_subscription tool.
  Should say: "I can't process subscription cancellations directly.
              I'm escalating you to a human agent."
Transcript showing tool routing and grounded response
User:    "Where is order A-12489?"

Agent decision: call_tool: get_order_status({"order_id": "A-12489"})

Tool result:    {"order_id": "A-12489", "status": "shipped",
                 "carrier": "DHL", "tracking": "JD0123456789",
                 "eta": "2026-06-25"}

Agent:   Your order A-12489 was shipped via DHL
         (tracking JD0123456789) and is scheduled to arrive on
         June 25, 2026. Anything else?
Datasets
A small policy knowledge base (hand-written)
Write 5–10 short policy pages (return policy, shipping, payments, warranty, contact). Saves as markdown files.

How to get it: Team writes them. Roughly 1 page each, ~300 words.

A fake orders database (hand-written)
A JSON file with 20 fake orders (order_id, items, status, carrier, tracking, eta). The get_order_status tool reads from this file.

How to get it: Write a Python function get_order_status(order_id) that reads the JSON. That is the entire "API".

A test scenario set
Write 20 test prompts: 8 policy questions, 8 order-status questions, 4 out-of-scope / escalation cases.

How to get it: Team writes them. JSON format with expected behaviour (which tool, or escalation).

Tools you'll need
These are suggestions, not requirements. If your team is more comfortable with a different library, model, or framework that achieves the same goal, use it — and briefly explain the choice in your README.

Python: Python 3.10 or newer. Compute: No GPU. A laptop is enough.

LLM with tool use
openai — Function-calling API. Define tools as JSON schemas; the model returns structured tool-call requests.
anthropic — Same idea, slightly different shape. Both work.
Knowledge base retrieval
sentence-transformers — Embed the policy pages.
chromadb — Tiny vector store for the policy KB.
UI
streamlit — Chat UI plus a side panel that shows which tool was called.
Secrets
python-dotenv — API key handling.
How to approach it
One reasonable path through the project. Specific tools (UMAP, HDBSCAN, BERTopic, etc.) are examples — feel free to swap them for alternatives you know better.

Build the policy KB. Chunk the policy markdown into ~300-token pieces, embed, index in ChromaDB.
Build the fake orders DB. Hand-write 20 orders into a JSON file.
Define the tools. Two tools: search_policy(query) returns the top-3 policy chunks; get_order_status(order_id) returns the order JSON.
Write the system prompt. Explain the agent's role, scope, and the escalation rule ("If you cannot answer with the tools you have, say so and escalate — do not invent.").
Build the agent loop. Send (system + history + user) to the LLM with the tools attached. If it requests a tool call, execute it locally and feed the result back. Repeat until the LLM produces a final answer.
Build the UI. Streamlit chat. Show the tool call(s) made for each turn in a collapsible panel.
Run the test set. For each scenario, check: did the agent call the right tool? Did it answer correctly? Did it escalate when it should?
Iterate. Tighten the system prompt where the agent misbehaves.
What to deliver
A Streamlit chat app with a side panel showing the tools called.
A scenario test set (20 prompts) with the team's per-scenario evaluation.
A README documenting the policies, the tool schema, and the escalation policy.

---

Proposed Architecture

Frontend - React + shadcn
Backend - FastAPI

Relational database (Postgres)
- Products (from @data/products.json)
- Orders
- Users

Embeddings database (Chromadb)
- Products collection (name + description)
- Policy/Policies (chunked) 

Agentic framework LangChain (https://docs.langchain.com/oss/python/langchain/agents)

Example System Prompt:
```
if the query is a general question about order policy, use only policy 
specific tools : [search_policy]
if the query is a specific question about a specific order, ask the 
order id and use only order specific tools

Do not give information about order until customer give you order ID
and names.

You cannot make actions on orders, you can only give information 
about it
```

On startup - the database shall be loaded with products from products.json into both the relational and vector database. The policy shall be chunked and ingested into the vector database. This operation shall only happen on the first startup (keep track or query to see if the table/collection are not empty before starting this process).

The backend shall implement standard REST APIs, and database access shall follow the Repository access design pattern.

The system shall be runnable locally via Docker Compose.

The agent's response shall be streamed (token by token).
---
Use cases:
- Users can sign up and sign in. This is a demo project so no need to invest in the complexity of the auth system. Do the bear minimum to allow sign, sign up, and long-lived sessions.

- Users can browse products catalog, add to cart, checkout, cancel order etc.
- Orders placed in the database for more than 30 seconds are automatically transitioned into out for delivery (for the sake of demos)
- Users can converse with the agent regarding their order status, ask questions about company policy and refund policy, but cannot perform any actions via the chatbot. The agent shall refuse to perform actions.
- The agent shall have tools search_policy(query) and get_order_status(order_id). When the agent is bootstrap with tools, the tools for a given conversation must be bound to a specific user, meaning that it should not be allowed for a user to lookup order status of other users.
---