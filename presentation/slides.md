---
theme: default
title: ShopEase — Customer Support Agent
info: >
  A LangGraph ReAct agent that handles common e-commerce support queries
  automatically. Built with FastAPI, ChromaDB, PostgreSQL, and GPT-4o-mini.
class: text-center
highlighter: shiki
drawings:
  persist: false
transition: slide-left
colorSchema: light
minimap: false
fonts:
  sans: Inter
  mono: Fira Code
contextMenu: false
---

<div class="flex flex-col items-center justify-center h-full gap-5 select-none">
  <div class="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-400">Academic Project · June 2026</div>
  <h1 class="text-6xl font-bold leading-tight text-gray-900 max-w-2xl">
    ShopEase<br/>Customer Support Agent
  </h1>
  <p class="text-xl text-gray-400 max-w-lg mt-1">
    Automating common e-commerce support queries<br/>with a LangGraph ReAct agent
  </p>
  <div class="flex gap-3 mt-4 flex-wrap justify-center">
    <span class="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-medium border border-indigo-100">FastAPI</span>
    <span class="px-3 py-1 bg-violet-50 text-violet-700 rounded-full text-xs font-medium border border-violet-100">LangGraph</span>
    <span class="px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium border border-emerald-100">ChromaDB</span>
    <span class="px-3 py-1 bg-amber-50 text-amber-700 rounded-full text-xs font-medium border border-amber-100">GPT-4o-mini</span>
    <span class="px-3 py-1 bg-sky-50 text-sky-700 rounded-full text-xs font-medium border border-sky-100">PostgreSQL</span>
  </div>
</div>

---
layout: center
class: text-center
---

# Outline

<div class="grid grid-cols-2 gap-4 mt-8 text-left max-w-2xl mx-auto">
  <div class="bg-indigo-50 rounded-xl p-5 border border-indigo-100">
    <div class="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-1">01</div>
    <div class="font-semibold text-indigo-900">Problem & Approach</div>
    <div class="text-sm text-gray-500 mt-1">Why this agent, and what it does</div>
  </div>
  <div class="bg-violet-50 rounded-xl p-5 border border-violet-100">
    <div class="text-xs font-bold uppercase tracking-wider text-violet-400 mb-1">02</div>
    <div class="font-semibold text-violet-900">Architecture</div>
    <div class="text-sm text-gray-500 mt-1">Stack, agent design, and data flow</div>
  </div>
  <div class="bg-emerald-50 rounded-xl p-5 border border-emerald-100">
    <div class="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-1">03</div>
    <div class="font-semibold text-emerald-900">Evaluation</div>
    <div class="text-sm text-gray-500 mt-1">30 scenarios across 3 categories</div>
  </div>
  <div class="bg-orange-50 rounded-xl p-5 border border-orange-100">
    <div class="text-xs font-bold uppercase tracking-wider text-orange-400 mb-1">04</div>
    <div class="font-semibold text-orange-900">Limitations & Next Steps</div>
    <div class="text-sm text-gray-500 mt-1">What the system can't do yet</div>
  </div>
</div>

---
layout: center
class: text-center
---

<div class="section-divider">
  <div class="section-number">01</div>
  <h1>Problem &<br/>Approach</h1>
</div>

---

# Support teams spend most of their time on the same questions

Not every support ticket needs a human.

<div class="grid grid-cols-2 gap-8 mt-6">
  <div v-click>
    <h3 class="font-semibold text-gray-700 mb-4">What customers actually ask</h3>
    <div class="space-y-2 text-sm">
      <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
        <mdi-package-variant-closed class="text-indigo-400 text-xl" />
        <span class="text-gray-700">"Where is my order A12345?"</span>
      </div>
      <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
        <mdi-arrow-u-left-bottom class="text-indigo-400 text-xl" />
        <span class="text-gray-700">"How do I return a sale item?"</span>
      </div>
      <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
        <mdi-shield-outline class="text-indigo-400 text-xl" />
        <span class="text-gray-700">"What warranty does my laptop have?"</span>
      </div>
      <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
        <mdi-airplane class="text-indigo-400 text-xl" />
        <span class="text-gray-700">"Do you ship to Europe?"</span>
      </div>
    </div>
  </div>
  <div v-click>
    <h3 class="font-semibold text-gray-700 mb-4">What these have in common</h3>
    <div class="space-y-3 text-sm">
      <div class="flex gap-3 items-start">
        <span class="text-emerald-500 font-bold text-base mt-0.5">✓</span>
        <span class="text-gray-600">The answer comes from a policy document or a database, not judgment</span>
      </div>
      <div class="flex gap-3 items-start">
        <span class="text-emerald-500 font-bold text-base mt-0.5">✓</span>
        <span class="text-gray-600">No human decision is needed — just retrieval</span>
      </div>
      <div class="flex gap-3 items-start">
        <span class="text-emerald-500 font-bold text-base mt-0.5">✓</span>
        <span class="text-gray-600">Customers want an answer in seconds</span>
      </div>
    </div>
    <div class="mt-5 p-4 bg-indigo-50 rounded-xl border border-indigo-100 text-sm text-indigo-800">
      An LLM that can search policy documents and query a database can handle most of these automatically — without a human in the loop.
    </div>
  </div>
</div>

---

# What we built

ShopEase is a fictional online store with a fully integrated AI support chat.

<div class="grid grid-cols-2 gap-8 mt-6">
  <div>
    <h3 class="font-semibold text-gray-700 mb-4">The application</h3>
    <div class="space-y-2.5 text-sm">
      <div class="flex gap-3 items-start p-2.5 rounded-lg hover:bg-gray-50 transition-colors">
        <span class="text-indigo-400 font-bold mt-0.5">→</span>
        <span class="text-gray-600">194 products with categories, cart, and checkout</span>
      </div>
      <div class="flex gap-3 items-start p-2.5 rounded-lg hover:bg-gray-50 transition-colors">
        <span class="text-indigo-400 font-bold mt-0.5">→</span>
        <span class="text-gray-600">Order tracking with automatic lifecycle advancement every 30 seconds</span>
      </div>
      <div class="flex gap-3 items-start p-2.5 rounded-lg hover:bg-gray-50 transition-colors">
        <span class="text-indigo-400 font-bold mt-0.5">→</span>
        <span class="text-gray-600">JWT auth with two modes: guest and authenticated</span>
      </div>
      <div class="flex gap-3 items-start p-2.5 rounded-lg hover:bg-gray-50 transition-colors">
        <span class="text-indigo-400 font-bold mt-0.5">→</span>
        <span class="text-gray-600">Streamed chat with a real-time tool-call panel</span>
      </div>
    </div>
  </div>
  <div>
    <h3 class="font-semibold text-gray-700 mb-4">Stack</h3>
    <div class="space-y-2 text-sm" v-click>
      <div class="flex justify-between items-center py-2 border-b border-gray-100">
        <span class="text-gray-500">Frontend</span>
        <code class="text-xs bg-gray-100 px-2.5 py-1 rounded-md text-gray-700">React 18 + Vite + Tailwind</code>
      </div>
      <div class="flex justify-between items-center py-2 border-b border-gray-100">
        <span class="text-gray-500">Backend</span>
        <code class="text-xs bg-gray-100 px-2.5 py-1 rounded-md text-gray-700">FastAPI + async SQLAlchemy</code>
      </div>
      <div class="flex justify-between items-center py-2 border-b border-gray-100">
        <span class="text-gray-500">Database</span>
        <code class="text-xs bg-gray-100 px-2.5 py-1 rounded-md text-gray-700">PostgreSQL 16</code>
      </div>
      <div class="flex justify-between items-center py-2 border-b border-gray-100">
        <span class="text-gray-500">Vector store</span>
        <code class="text-xs bg-gray-100 px-2.5 py-1 rounded-md text-gray-700">ChromaDB + text-embedding-3-small</code>
      </div>
      <div class="flex justify-between items-center py-2 border-b border-gray-100">
        <span class="text-gray-500">Agent</span>
        <code class="text-xs bg-gray-100 px-2.5 py-1 rounded-md text-gray-700">LangGraph ReAct + GPT-4o-mini</code>
      </div>
      <div class="flex justify-between items-center py-2">
        <span class="text-gray-500">Alt. LLM</span>
        <code class="text-xs bg-gray-100 px-2.5 py-1 rounded-md text-gray-700">Ollama + Qwen Coder Instruct</code>
      </div>
    </div>
  </div>
</div>

---
layout: center
class: text-center
---

<div class="section-divider section-divider--violet">
  <div class="section-number">02</div>
  <h1>Architecture</h1>
</div>

---

# System architecture

<div class="flex justify-center mt-2">
  <img
    src="./images/system-architecture-white-background.png"
    class="max-h-88 rounded-2xl shadow-lg border border-gray-200 object-contain"
  />
</div>

<div v-click class="mt-4 flex justify-center">
  <div class="text-sm text-gray-500 bg-gray-50 rounded-lg px-5 py-2.5 border border-gray-100 max-w-2xl text-center">
    The agent runs a <strong class="text-gray-700">ReAct loop</strong> — reason about the message, call a tool, reason about the result, repeat until it has enough to respond.
  </div>
</div>

---

# Agent design

<div class="grid grid-cols-2 gap-6 mt-6">
  <div>
    <h3 class="font-semibold text-gray-700 mb-4">Two user modes</h3>
    <div v-click class="space-y-3 text-sm">
      <div class="p-4 bg-gray-50 rounded-xl border border-gray-200">
        <div class="font-medium text-gray-700">Guest</div>
        <div class="text-gray-500 mt-1">Policy search, product search, product lookup by ID. No order access.</div>
      </div>
      <div class="p-4 bg-indigo-50 rounded-xl border border-indigo-200">
        <div class="font-medium text-indigo-700">Authenticated</div>
        <div class="text-indigo-600 mt-1">All guest tools + order status lookup + full order history.</div>
      </div>
    </div>
    <div v-click class="mt-4 p-3.5 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-800">
      <strong>User scoping:</strong> order tools are built via closure at request time. The <code>user_id</code> is captured inside the function — never passed as an argument. Querying another user's data isn't a validation problem; it's structurally not possible.
    </div>
  </div>
  <div>
    <h3 class="font-semibold text-gray-700 mb-4">Routing (from the system prompt)</h3>
    <div v-click class="text-xs font-mono bg-gray-950 text-green-400 rounded-xl p-5 space-y-2 leading-relaxed">
      <div class="text-gray-500"># policy, shipping, returns, payments</div>
      <div>→ search_policy(query)</div>
      <div class="mt-1 text-gray-500"># "do you sell X?", product search</div>
      <div>→ search_products(query)</div>
      <div class="mt-1 text-gray-500"># "show my orders"</div>
      <div>→ get_order_history()</div>
      <div class="mt-1 text-gray-500"># "where is order A12345?"</div>
      <div>→ get_order_status(order_id)</div>
      <div class="mt-1 text-gray-500"># "cancel my order / refund me"</div>
      <div>→ <span class="text-red-400">escalate to human</span></div>
    </div>
  </div>
</div>

---

# Tools and data sources

<div class="mt-2 text-sm">

| Tool | Access | Source | Detail |
|------|--------|--------|--------|
| `search_policy(query)` | Guest + Auth | ChromaDB | 7 policy docs · top-3 chunks |
| `search_products(query)` | Guest + Auth | ChromaDB | 194 products · top-5 results |
| `get_products_by_id(ids)` | Guest + Auth | PostgreSQL | Direct ID lookup · includes stock |
| `get_order_status(order_id)` | Auth only | PostgreSQL | User-scoped · carrier + ETA |
| `get_order_history()` | Auth only | PostgreSQL | All orders · most-recent first |

</div>

<div class="grid grid-cols-2 gap-4 mt-5 text-sm">
  <div v-click class="p-4 bg-indigo-50 rounded-xl border border-indigo-100">
    <strong class="text-indigo-800">ChromaDB</strong>
    <div class="text-gray-600 mt-1.5">
      Policy documents and product descriptions embedded at startup with <code>text-embedding-3-small</code>. Similarity search at query time.
    </div>
  </div>
  <div v-click class="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
    <strong class="text-emerald-800">PostgreSQL</strong>
    <div class="text-gray-600 mt-1.5">
      Three tables: Users, Products, Orders. A background job advances each order one stage every 30 seconds — from <code>created</code> to <code>delivered</code>.
    </div>
  </div>
</div>

---
layout: center
class: text-center
---

<div class="section-divider section-divider--emerald">
  <div class="section-number">03</div>
  <h1>Evaluation</h1>
</div>

---

# Evaluation approach

<div class="grid grid-cols-2 gap-8 mt-6">

<div>
  <h3 class="font-semibold text-gray-700 mb-4">What we measure</h3>
  <div class="space-y-3 text-sm">
    <div class="p-3.5 bg-gray-50 rounded-xl border-l-4 border-indigo-500">
      <strong>Tool selection</strong> — did the agent call the expected tool?
      <div class="text-gray-500 mt-1">Deterministic: binary pass / fail per scenario.</div>
    </div>
    <div class="p-3.5 bg-gray-50 rounded-xl border-l-4 border-emerald-500">
      <strong>Behavioral correctness</strong> — did it ask for a missing order ID? Did it escalate when it couldn't help?
      <div class="text-gray-500 mt-1">Checked with keyword matching on the final response.</div>
    </div>
    <div class="p-3.5 bg-gray-50 rounded-xl border-l-4 border-violet-500">
      <strong>No hallucination</strong> — did the agent invent information when tools returned nothing?
      <div class="text-gray-500 mt-1">Verified by checking the response is non-empty and grounded in tool output.</div>
    </div>
  </div>
</div>

<div>
  <h3 class="font-semibold text-gray-700 mb-4">How the harness works</h3>
  <div v-click class="text-sm text-gray-600 space-y-2">
    <p>The script loads 30 scenarios from <code>scenarios.json</code>, sends each conversation to the live <code>/api/v1/chat/stream</code> endpoint, and collects the streamed tool calls and final text.</p>
    <p class="mt-2">Each scenario specifies the expected tool, expected behavior, and whether escalation should trigger.</p>
    <div class="mt-3 font-mono text-xs bg-gray-950 text-green-400 rounded-xl p-4 leading-relaxed">
      <span class="text-gray-500"># Run all 30 scenarios</span><br/>
      python tests/eval.py --token "$TOKEN"<br/><br/>
      <span class="text-gray-500"># Filter by category</span><br/>
      python tests/eval.py --token "$TOKEN" \<br/>
      &nbsp;&nbsp;--category policy
    </div>
  </div>
</div>

</div>

---

# 30 scenarios across 3 categories

<div class="grid grid-cols-3 gap-4 mt-5">

<div v-click class="bg-indigo-50 border border-indigo-100 rounded-2xl p-4">
<div class="font-semibold text-indigo-800 mb-3 text-sm">Policy · 12 scenarios</div>
<div class="text-xs space-y-1.5 text-gray-600">
  <div class="p-2 bg-white rounded-lg border border-indigo-50">Return window — 30 days</div>
  <div class="p-2 bg-white rounded-lg border border-indigo-50">Sale items → store credit only</div>
  <div class="p-2 bg-white rounded-lg border border-indigo-50">International shipping zones</div>
  <div class="p-2 bg-white rounded-lg border border-indigo-50">Free shipping at $50</div>
  <div class="p-2 bg-white rounded-lg border border-indigo-50">Payment methods + BNPL</div>
  <div class="p-2 bg-white rounded-lg border border-indigo-50">Laptop warranty (1 year)</div>
  <div class="p-2 bg-white rounded-lg border border-indigo-50">Non-returnable items</div>
  <div class="p-2 bg-white rounded-lg border border-indigo-50">Data deletion rights</div>
</div>
</div>

<div v-click class="bg-emerald-50 border border-emerald-100 rounded-2xl p-4">
<div class="font-semibold text-emerald-800 mb-3 text-sm">Order · 12 scenarios</div>
<div class="text-xs space-y-1.5 text-gray-600">
  <div class="p-2 bg-white rounded-lg border border-emerald-50">Lookup with valid order code</div>
  <div class="p-2 bg-white rounded-lg border border-emerald-50">Missing ID → agent asks first</div>
  <div class="p-2 bg-white rounded-lg border border-emerald-50">Multi-turn ID collection</div>
  <div class="p-2 bg-white rounded-lg border border-emerald-50">Non-existent order code</div>
  <div class="p-2 bg-white rounded-lg border border-emerald-50">Tracking number + ETA</div>
  <div class="p-2 bg-white rounded-lg border border-emerald-50">Lowercase code handling</div>
  <div class="p-2 bg-white rounded-lg border border-emerald-50">Two orders in one message</div>
  <div class="p-2 bg-white rounded-lg border border-emerald-50">Cross-user access denial</div>
</div>
</div>

<div v-click class="bg-orange-50 border border-orange-100 rounded-2xl p-4">
<div class="font-semibold text-orange-800 mb-3 text-sm">Escalation · 6 scenarios</div>
<div class="text-xs space-y-1.5 text-gray-600">
  <div class="p-2 bg-white rounded-lg border border-orange-50">Cancel subscription + refund</div>
  <div class="p-2 bg-white rounded-lg border border-orange-50">Process a refund immediately</div>
  <div class="p-2 bg-white rounded-lg border border-orange-50">Modify a shipping address</div>
  <div class="p-2 bg-white rounded-lg border border-orange-50">Off-topic request (poem)</div>
  <div class="p-2 bg-white rounded-lg border border-orange-50">Explicit human agent request</div>
  <div class="p-2 bg-white rounded-lg border border-orange-50">Fraud / account compromise</div>
</div>
</div>

</div>

---

# What the evaluation misses

Deterministic testing covers tool selection reliably. Response quality is a harder problem.

<div class="grid grid-cols-2 gap-8 mt-6">

<div v-click>
<h3 class="font-semibold text-gray-700 mb-3">What's reliable</h3>
<div class="space-y-2 text-sm text-gray-600">
  <div class="flex gap-2.5 items-start">
    <span class="text-emerald-500 font-bold">✓</span>
    <span>The agent called <code>search_policy</code> — or didn't</span>
  </div>
  <div class="flex gap-2.5 items-start">
    <span class="text-emerald-500 font-bold">✓</span>
    <span>The response contains "escalating" when it should</span>
  </div>
  <div class="flex gap-2.5 items-start">
    <span class="text-emerald-500 font-bold">✓</span>
    <span>The agent asked for an order ID before calling the order tool</span>
  </div>
  <div class="flex gap-2.5 items-start">
    <span class="text-emerald-500 font-bold">✓</span>
    <span>The response was non-empty</span>
  </div>
</div>
</div>

<div v-click>
<h3 class="font-semibold text-gray-700 mb-3">What it misses</h3>
<div class="space-y-2 text-sm text-gray-600">
  <div class="flex gap-2.5 items-start">
    <span class="text-red-400 font-bold">✗</span>
    <span>Did it quote the correct return window (30 days), or just some policy text?</span>
  </div>
  <div class="flex gap-2.5 items-start">
    <span class="text-red-400 font-bold">✗</span>
    <span>Was the response clear, or technically accurate but confusing?</span>
  </div>
  <div class="flex gap-2.5 items-start">
    <span class="text-red-400 font-bold">✗</span>
    <span>Did it give the right carrier and ETA, or just a valid-looking response?</span>
  </div>
</div>

<div class="mt-4 p-3.5 bg-yellow-50 rounded-xl border border-yellow-200 text-xs text-yellow-800">
  Closing this gap requires a second evaluation pass: either human review or LLM-as-a-Judge with a reference answer per scenario.
</div>
</div>

</div>

---
layout: center
class: text-center
---

<div class="section-divider section-divider--red">
  <div class="section-number">04</div>
  <h1>Limitations &<br/>Next Steps</h1>
</div>

---

# Limitations

<div class="space-y-4 mt-5">

<div v-click class="flex gap-4 p-4 bg-red-50 rounded-xl border border-red-200">
  <div class="flex-shrink-0"><mdi-currency-usd class="text-2xl text-red-400" /></div>
  <div>
    <div class="font-semibold text-gray-800">Cost at scale</div>
    <div class="text-sm text-gray-600 mt-1">
      GPT-4o-mini charges per token. That's negligible in a demo, but at real support volume it compounds. Switching to an open-source model via Ollama removes the per-token cost — but open-source models are less consistent at following instructions, particularly for multi-step reasoning. Both options are in the codebase; the trade-off is real.
    </div>
  </div>
</div>

<div v-click class="flex gap-4 p-4 bg-orange-50 rounded-xl border border-orange-200">
  <div class="flex-shrink-0"><mdi-lock-outline class="text-2xl text-orange-400" /></div>
  <div>
    <div class="font-semibold text-gray-800">Security</div>
    <div class="text-sm text-gray-600 mt-1">
      The system prompt sets guardrails, but LLMs can be manipulated through prompt injection. A malicious message could try to override the agent's behavior. The agent also has access to full order history, which makes a successful jailbreak more damaging than it would be on a stateless chatbot.
    </div>
  </div>
</div>

<div v-click class="flex gap-4 p-4 bg-blue-50 rounded-xl border border-blue-200">
  <div class="flex-shrink-0"><mdi-clipboard-list-outline class="text-2xl text-blue-400" /></div>
  <div>
    <div class="font-semibold text-gray-800">Read-only scope</div>
    <div class="text-sm text-gray-600 mt-1">
      The agent retrieves information but cannot take action. Refunds, cancellations, and address changes still need a human. This was intentional — a write-capable agent needs much more careful guardrails — but it limits how much of the support queue it can actually close.
    </div>
  </div>
</div>

</div>

---

# Next steps

<div class="grid grid-cols-2 gap-5 mt-6">

<div v-click class="contents">
  <div class="bg-gray-50 border border-gray-200 rounded-xl p-5 hover:border-indigo-200 hover:bg-indigo-50 transition-colors">
    <div class="font-semibold text-gray-800 mb-2">Agentic actions</div>
    <div class="text-sm text-gray-600">
      Give the agent tools to cancel eligible orders or initiate returns, with a confirmation step before committing. This would close the gap between "explaining the refund policy" and "starting the refund."
    </div>
  </div>
  <div class="bg-gray-50 border border-gray-200 rounded-xl p-5 hover:border-emerald-200 hover:bg-emerald-50 transition-colors">
    <div class="font-semibold text-gray-800 mb-2">Open-source model benchmark</div>
    <div class="text-sm text-gray-600">
      Run the full 30-scenario suite against Qwen and Llama via Ollama. Get concrete numbers on how much accuracy changes when you remove the per-token cost. The gap probably varies across scenario categories.
    </div>
  </div>
</div>

<div v-click class="contents">
  <div class="bg-gray-50 border border-gray-200 rounded-xl p-5 hover:border-violet-200 hover:bg-violet-50 transition-colors">
    <div class="font-semibold text-gray-800 mb-2">LLM-as-a-Judge</div>
    <div class="text-sm text-gray-600">
      Add a second LLM call that reads the agent's response and the expected answer, then scores it for accuracy and completeness. This directly addresses the quality gap that keyword-based checks can't reach.
    </div>
  </div>
  <div class="bg-gray-50 border border-gray-200 rounded-xl p-5 hover:border-amber-200 hover:bg-amber-50 transition-colors">
    <div class="font-semibold text-gray-800 mb-2">Session memory</div>
    <div class="text-sm text-gray-600">
      The current implementation sends the full conversation history on each request but doesn't persist across page reloads. A session store would let customers continue interrupted conversations without repeating themselves.
    </div>
  </div>
</div>

</div>

---
layout: center
class: text-center
---

# The Team

<div class="grid grid-cols-5 gap-6 mt-8 max-w-4xl mx-auto">

  <div class="flex flex-col items-center gap-3">
    <img src="./images/team/raounek.png" class="w-24 h-24 rounded-full object-cover border-2 border-indigo-100 shadow-md" />
    <div>
      <div class="font-semibold text-gray-800 text-sm leading-tight">Raounek Zeghdoud</div>
      <div class="text-xs text-gray-400 mt-1">Mines Paris – PSL</div>
    </div>
  </div>

  <div class="flex flex-col items-center gap-3">
    <div class="w-24 h-24 rounded-full border-2 border-gray-200 shadow-md overflow-hidden flex-shrink-0">
      <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
        <rect width="100" height="100" fill="#f1f5f9"/>
        <circle cx="50" cy="37" r="19" fill="#cbd5e1"/>
        <ellipse cx="50" cy="85" rx="30" ry="23" fill="#cbd5e1"/>
      </svg>
    </div>
    <div>
      <div class="font-semibold text-gray-800 text-sm leading-tight">Nada Alrehaili</div>
      <div class="text-xs text-gray-400 mt-1">University of Liverpool</div>
    </div>
  </div>

  <div class="flex flex-col items-center gap-3">
    <img src="./images/team/solene.png" class="w-24 h-24 rounded-full object-cover border-2 border-indigo-100 shadow-md" />
    <div>
      <div class="font-semibold text-gray-800 text-sm leading-tight">Solène Delourme</div>
      <div class="text-xs text-gray-400 mt-1">CentraleSupélec</div>
    </div>
  </div>

  <div class="flex flex-col items-center gap-3">
    <img src="./images/team/antonio.png" class="w-24 h-24 rounded-full object-cover border-2 border-indigo-100 shadow-md" />
    <div>
      <div class="font-semibold text-gray-800 text-sm leading-tight">Antonio Zaitoun</div>
      <div class="text-xs text-gray-400 mt-1">University of Haifa</div>
    </div>
  </div>

  <div class="flex flex-col items-center gap-3">
    <img src="./images/team/donatas.png" class="w-24 h-24 rounded-full object-cover border-2 border-indigo-100 shadow-md" />
    <div>
      <div class="font-semibold text-gray-800 text-sm leading-tight">Donatas Iliška</div>
      <div class="text-xs text-gray-400 mt-1">Kaunas University of Technology</div>
    </div>
  </div>

</div>

---
layout: center
class: text-center
---

<div class="flex flex-col items-center justify-center h-full gap-6">
  <div class="text-6xl font-bold text-gray-900">Thank you</div>
  <div class="text-xl text-gray-400">Questions?</div>
  <div class="mt-6 grid grid-cols-3 gap-4 max-w-xl">
    <div class="p-3.5 bg-indigo-50 rounded-xl text-center border border-indigo-100">
      <div class="text-xs font-mono text-indigo-400 mb-1">Backend</div>
      <div class="text-sm text-indigo-800 font-medium">FastAPI + LangGraph</div>
    </div>
    <div class="p-3.5 bg-violet-50 rounded-xl text-center border border-violet-100">
      <div class="text-xs font-mono text-violet-400 mb-1">Frontend</div>
      <div class="text-sm text-violet-800 font-medium">React + Tailwind</div>
    </div>
    <div class="p-3.5 bg-amber-50 rounded-xl text-center border border-amber-100">
      <div class="text-xs font-mono text-amber-400 mb-1">Agent</div>
      <div class="text-sm text-amber-800 font-medium">GPT-4o-mini · ReAct</div>
    </div>
  </div>
</div>
