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

<div class="absolute top-10 left-1/2 -translate-x-1/2 flex items-center gap-10 opacity-80 select-none">
  <img src="./images/logos/sapienza.png" class="h-11 object-contain" alt="Sapienza Università di Roma" />
  <div class="w-px h-9 bg-gray-200"></div>
  <img src="./images/logos/program.png" class="h-11 object-contain" alt="GenAI School" />
</div>

<div class="flex flex-col items-center justify-center h-full gap-4 select-none">
  <div class="flex items-center gap-3 text-gray-900">
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M16 10a4 4 0 0 1-8 0M3.103 6.034h17.794"/><path d="M3.4 5.467a2 2 0 0 0-.4 1.2V20a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6.667a2 2 0 0 0-.4-1.2l-2-2.667A2 2 0 0 0 17 2H7a2 2 0 0 0-1.6.8z"/></svg>
    <span class="text-7xl font-bold tracking-tight">ShopEase</span>
  </div>
  <p class="text-2xl text-gray-400 font-medium">Customer Support Agent</p>
  <div class="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-400 mt-2">The International Summer School on Generative AI</div>
</div>

<div class="marquee absolute bottom-8 left-0 right-0 select-none">
  <div class="marquee__track">
    <TechStrip />
    <TechStrip />
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
    <div class="text-sm text-gray-500 mt-1">30 scenarios · 97% tool accuracy · LLM-as-Judge</div>
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
      An agent that can search policy documents and query a database can handle most of these automatically — without a human in the loop.
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
    <div class="space-y-1.5 text-sm" v-click>
      <div class="flex justify-between items-center py-1.5 border-b border-gray-100">
        <span class="text-gray-500 shrink-0">Frontend</span>
        <div class="flex gap-1.5 items-center flex-wrap justify-end">
          <span class="flex items-center gap-1 text-xs bg-sky-50 text-sky-700 px-2 py-0.5 rounded-md border border-sky-100 font-medium"><React :size="14" /> React 18</span>
          <span class="flex items-center gap-1 text-xs bg-purple-50 text-purple-700 px-2 py-0.5 rounded-md border border-purple-100 font-medium"><Vite :size="14" /> Vite</span>
          <span class="flex items-center gap-1 text-xs bg-cyan-50 text-cyan-700 px-2 py-0.5 rounded-md border border-cyan-100 font-medium"><TailwindCss :size="14" /> Tailwind</span>
        </div>
      </div>
      <div class="flex justify-between items-center py-1.5 border-b border-gray-100">
        <span class="text-gray-500 shrink-0">Backend</span>
        <div class="flex gap-1.5 items-center flex-wrap justify-end">
          <span class="flex items-center gap-1 text-xs bg-teal-50 text-teal-700 px-2 py-0.5 rounded-md border border-teal-100 font-medium"><Fastapi :size="14" /> FastAPI</span>
          <span class="flex items-center gap-1 text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-md border border-red-100 font-medium"><Sqlalchemy :size="14" /> SQLAlchemy</span>
        </div>
      </div>
      <div class="flex justify-between items-center py-1.5 border-b border-gray-100">
        <span class="text-gray-500 shrink-0">Database</span>
        <div class="flex gap-1.5 items-center justify-end">
          <span class="flex items-center gap-1 text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-md border border-blue-100 font-medium"><Postgresql :size="14" /> PostgreSQL 16</span>
        </div>
      </div>
      <div class="flex justify-between items-center py-1.5 border-b border-gray-100">
        <span class="text-gray-500 shrink-0">Vector store</span>
        <div class="flex gap-1.5 items-center flex-wrap justify-end">
          <span class="flex items-center gap-1 text-xs bg-violet-50 text-violet-700 px-2 py-0.5 rounded-md border border-violet-100 font-medium"><Chroma :size="14" /> ChromaDB</span>
          <span class="flex items-center gap-1 text-xs bg-gray-50 text-gray-600 px-2 py-0.5 rounded-md border border-gray-200 font-medium"><Openai :size="14" variant="light" /> text-embedding-3-small</span>
        </div>
      </div>
      <div class="flex justify-between items-center py-1.5 border-b border-gray-100">
        <span class="text-gray-500 shrink-0">Agent</span>
        <div class="flex gap-1.5 items-center flex-wrap justify-end">
          <span class="flex items-center gap-1 text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-md border border-emerald-100 font-medium"><Langgraph :size="14" /> LangGraph ReAct</span>
          <span class="flex items-center gap-1 text-xs bg-gray-50 text-gray-600 px-2 py-0.5 rounded-md border border-gray-200 font-medium"><Openai :size="14" variant="light" /> GPT-4o-mini</span>
        </div>
      </div>
      <div class="flex justify-between items-center py-1.5">
        <span class="text-gray-500 shrink-0">Alt. LLM</span>
        <div class="flex gap-1.5 items-center flex-wrap justify-end">
          <span class="flex items-center gap-1 text-xs bg-orange-50 text-orange-700 px-2 py-0.5 rounded-md border border-orange-100 font-medium"><Ollama :size="14" /> Ollama</span>
          <span class="flex items-center gap-1 text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-md border border-indigo-100 font-medium"><Qwen :size="14" variant="light" /> Qwen Coder</span>
        </div>
      </div>
    </div>
  </div>
</div>

---
layout: center
class: text-center
---

# See it in action

---
layout: center
class: text-center
---

<div class="absolute inset-0 flex items-center justify-center p-3">
  <video
    src="./images/demo.mov"
    autoplay
    loop
    muted
    playsinline
    class="max-w-full max-h-full w-auto h-auto rounded-[28px] shadow-2xl border border-gray-200 object-contain"
  ></video>
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

<div class="mt-2 text-xs leading-tight">

| Tool | Access | Source | Detail |
|------|--------|--------|--------|
| `search_policy(query)` | Guest + Auth | ChromaDB | 7 policy docs · top-3 chunks |
| `search_products(query)` | Guest + Auth | ChromaDB | 194 products · top-5 results |
| `get_products_by_id(ids)` | Guest + Auth | PostgreSQL | Direct ID lookup · includes stock |
| `get_order_status(order_id)` | Auth only | PostgreSQL | User-scoped · carrier + ETA |
| `get_order_history()` | Auth only | PostgreSQL | All orders · most-recent first |
| `get_order_items(order_id)` | Auth only | PostgreSQL | Line items for a single order |
| `escalate_to_human(reason, order_id)` | Auth only | PostgreSQL | Hand off to a human · with order context |
| `escalate_to_human(reason)` | Guest | PostgreSQL | Hand off to a human · guest |

</div>

<div class="grid grid-cols-2 gap-3 mt-3 text-xs">
  <div v-click class="p-3 bg-indigo-50 rounded-xl border border-indigo-100">
    <strong class="text-indigo-800">ChromaDB</strong>
    <div class="text-gray-600 mt-1">
      Policy documents and product descriptions embedded at startup with <code>text-embedding-3-small</code>. Similarity search at query time.
    </div>
  </div>
  <div v-click class="p-3 bg-emerald-50 rounded-xl border border-emerald-100">
    <strong class="text-emerald-800">PostgreSQL</strong>
    <div class="text-gray-600 mt-1">
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

# 30 scenarios across 4 categories

<div class="grid grid-cols-4 gap-3 mt-4">

<div v-click class="bg-indigo-50 border border-indigo-100 rounded-2xl p-3">
<div class="font-semibold text-indigo-800 mb-2 text-sm">Policy · 6</div>
<div class="text-xs space-y-1 text-gray-600">
  <div class="px-2 py-1 bg-white rounded-md border border-indigo-50">Return policy</div>
  <div class="px-2 py-1 bg-white rounded-md border border-indigo-50">Free shipping</div>
  <div class="px-2 py-1 bg-white rounded-md border border-indigo-50">Warranty</div>
  <div class="px-2 py-1 bg-white rounded-md border border-indigo-50">Payment methods</div>
  <div class="px-2 py-1 bg-white rounded-md border border-indigo-50">No answer available</div>
  <div class="px-2 py-1 bg-white rounded-md border border-indigo-50">Guest question</div>
</div>
</div>

<div v-click class="bg-violet-50 border border-violet-100 rounded-2xl p-3">
<div class="font-semibold text-violet-800 mb-2 text-sm">Product · 6</div>
<div class="text-xs space-y-1 text-gray-600">
  <div class="px-2 py-1 bg-white rounded-md border border-violet-50">Search by keyword</div>
  <div class="px-2 py-1 bg-white rounded-md border border-violet-50">Search by category</div>
  <div class="px-2 py-1 bg-white rounded-md border border-violet-50">Product not sold</div>
  <div class="px-2 py-1 bg-white rounded-md border border-violet-50">Price/stock by id</div>
  <div class="px-2 py-1 bg-white rounded-md border border-violet-50">Search + details</div>
  <div class="px-2 py-1 bg-white rounded-md border border-violet-50">Out of scope</div>
</div>
</div>

<div v-click class="bg-emerald-50 border border-emerald-100 rounded-2xl p-3">
<div class="font-semibold text-emerald-800 mb-2 text-sm">Order · 11</div>
<div class="text-xs space-y-1 text-gray-600">
  <div class="px-2 py-1 bg-white rounded-md border border-emerald-50">Order status</div>
  <div class="px-2 py-1 bg-white rounded-md border border-emerald-50">Tracking number</div>
  <div class="px-2 py-1 bg-white rounded-md border border-emerald-50">ETA</div>
  <div class="px-2 py-1 bg-white rounded-md border border-emerald-50">History</div>
  <div class="px-2 py-1 bg-white rounded-md border border-emerald-50">Non-existent order</div>
  <div class="px-2 py-1 bg-white rounded-md border border-emerald-50">Status without ID</div>
  <div class="px-2 py-1 bg-white rounded-md border border-emerald-50">Cancel without ID</div>
  <div class="px-2 py-1 bg-white rounded-md border border-emerald-50">History + status</div>
  <div class="px-2 py-1 bg-white rounded-md border border-emerald-50">Status + policy</div>
  <div class="px-2 py-1 bg-white rounded-md border border-emerald-50">Items in one order</div>
  <div class="px-2 py-1 bg-white rounded-md border border-emerald-50">Items across orders</div>
</div>
</div>

<div v-click class="bg-orange-50 border border-orange-100 rounded-2xl p-3">
<div class="font-semibold text-orange-800 mb-2 text-sm">Escalation · 6</div>
<div class="text-xs space-y-1 text-gray-600">
  <div class="px-2 py-1 bg-white rounded-md border border-orange-50">Cancellation</div>
  <div class="px-2 py-1 bg-white rounded-md border border-orange-50">Refund</div>
  <div class="px-2 py-1 bg-white rounded-md border border-orange-50">Address change</div>
  <div class="px-2 py-1 bg-white rounded-md border border-orange-50">Human request</div>
  <div class="px-2 py-1 bg-white rounded-md border border-orange-50">Human request (guest)</div>
  <div class="px-2 py-1 bg-white rounded-md border border-orange-50">Cancel non-existent order</div>
</div>
</div>

</div>

---

# Evaluation results

<div class="grid grid-cols-4 gap-3 mt-3">
  <div class="bg-indigo-50 border border-indigo-100 rounded-xl p-3.5 text-center">
    <div class="text-4xl font-bold text-indigo-700 leading-none">30</div>
    <div class="text-xs text-indigo-400 font-medium mt-1.5 uppercase tracking-wide">scenarios</div>
  </div>
  <div class="bg-emerald-50 border border-emerald-100 rounded-xl p-3.5 text-center">
    <div class="text-4xl font-bold text-emerald-700 leading-none">97%</div>
    <div class="text-xs text-emerald-400 font-medium mt-1.5 uppercase tracking-wide">correct tool use</div>
  </div>
  <div class="bg-amber-50 border border-amber-100 rounded-xl p-3.5 text-center">
    <div class="text-4xl font-bold text-amber-600 leading-none">4.80<span class="text-xl text-amber-300 font-normal">/5</span></div>
    <div class="text-xs text-amber-400 font-medium mt-1.5 uppercase tracking-wide">best judge avg</div>
  </div>
  <div class="bg-violet-50 border border-violet-100 rounded-xl p-3.5 text-center">
    <div class="text-4xl font-bold text-violet-700 leading-none">3</div>
    <div class="text-xs text-violet-400 font-medium mt-1.5 uppercase tracking-wide">judge models</div>
  </div>
</div>

<div class="grid grid-cols-2 gap-6 mt-4">

<div>
  <div class="flex items-baseline gap-2 mb-2">
    <span class="text-xs font-bold uppercase tracking-widest text-gray-400">Execution</span>
    <span class="text-xs text-gray-400">· did the agent call the right tools?</span>
  </div>
  <div class="text-xs font-semibold text-gray-500 mb-1.5">By category</div>
  <div class="space-y-1.5 text-xs">
    <div class="flex items-center gap-2">
      <span class="w-20 text-gray-500 text-right shrink-0">Policy</span>
      <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden"><div class="h-full bg-emerald-500 rounded-full" style="width:100%"></div></div>
      <span class="text-emerald-600 font-semibold w-10 text-right">6/6</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="w-20 text-gray-500 text-right shrink-0">Product</span>
      <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden"><div class="h-full bg-emerald-500 rounded-full" style="width:100%"></div></div>
      <span class="text-emerald-600 font-semibold w-10 text-right">7/7</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="w-20 text-gray-500 text-right shrink-0">Order</span>
      <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden"><div class="h-full bg-emerald-500 rounded-full" style="width:91.7%"></div></div>
      <span class="text-amber-500 font-semibold w-10 text-right">11/12</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="w-20 text-gray-500 text-right shrink-0">Escalation</span>
      <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden"><div class="h-full bg-emerald-500 rounded-full" style="width:100%"></div></div>
      <span class="text-emerald-600 font-semibold w-10 text-right">5/5</span>
    </div>
  </div>
  <div class="text-xs font-semibold text-gray-500 mt-3 mb-1.5">By tool type</div>
  <div class="space-y-1.5 text-xs">
    <div class="flex items-center gap-2">
      <span class="w-20 text-gray-500 text-right shrink-0">Single tool</span>
      <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden"><div class="h-full bg-indigo-500 rounded-full" style="width:100%"></div></div>
      <span class="text-indigo-600 font-semibold w-10 text-right">21/21</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="w-20 text-gray-500 text-right shrink-0">Multi-tool</span>
      <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden"><div class="h-full bg-indigo-500 rounded-full" style="width:80%"></div></div>
      <span class="text-amber-500 font-semibold w-10 text-right">4/5</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="w-20 text-gray-500 text-right shrink-0">No tool</span>
      <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden"><div class="h-full bg-indigo-500 rounded-full" style="width:100%"></div></div>
      <span class="text-indigo-600 font-semibold w-10 text-right">4/4</span>
    </div>
  </div>
</div>

<div>
  <div class="flex items-baseline gap-2 mb-2">
    <span class="text-xs font-bold uppercase tracking-widest text-gray-400">Quality</span>
    <span class="text-xs text-gray-400">· LLM-as-Judge across 3 models</span>
  </div>
  <div class="text-xs font-semibold text-gray-500 mb-1.5">Overall score /5</div>
  <div class="space-y-2 text-xs">
    <div class="flex items-center gap-2">
      <span class="w-24 text-gray-500 text-right shrink-0">gpt-4o-mini</span>
      <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden"><div class="h-full bg-indigo-600 rounded-full" style="width:96%"></div></div>
      <span class="text-indigo-600 font-bold w-8">4.80</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="w-24 text-gray-500 text-right shrink-0">o3-mini</span>
      <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden"><div class="h-full bg-emerald-500 rounded-full" style="width:92.6%"></div></div>
      <span class="text-emerald-600 font-bold w-8">4.63</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="w-24 text-gray-500 text-right shrink-0">gpt-4o</span>
      <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden"><div class="h-full bg-amber-400 rounded-full" style="width:88.4%"></div></div>
      <span class="text-amber-500 font-bold w-8">4.42</span>
    </div>
  </div>
  <div class="text-xs font-semibold text-gray-500 mt-3 mb-2">By dimension</div>
  <div class="flex gap-3">
    <div class="flex-1 flex flex-col items-center gap-1">
      <div class="flex gap-0.5 items-end" style="height:48px">
        <div class="w-2.5 bg-indigo-600 rounded-t-sm" style="height:95%"></div>
        <div class="w-2.5 bg-emerald-500 rounded-t-sm" style="height:91%"></div>
        <div class="w-2.5 bg-amber-400 rounded-t-sm" style="height:84%"></div>
      </div>
      <span class="text-xs text-gray-500 text-center">Grounding</span>
    </div>
    <div class="flex-1 flex flex-col items-center gap-1">
      <div class="flex gap-0.5 items-end" style="height:48px">
        <div class="w-2.5 bg-indigo-600 rounded-t-sm" style="height:94%"></div>
        <div class="w-2.5 bg-emerald-500 rounded-t-sm" style="height:89%"></div>
        <div class="w-2.5 bg-amber-400 rounded-t-sm" style="height:83%"></div>
      </div>
      <span class="text-xs text-gray-500 text-center">Accuracy</span>
    </div>
    <div class="flex-1 flex flex-col items-center gap-1">
      <div class="flex gap-0.5 items-end" style="height:48px">
        <div class="w-2.5 bg-indigo-600 rounded-t-sm" style="height:94%"></div>
        <div class="w-2.5 bg-emerald-500 rounded-t-sm" style="height:91%"></div>
        <div class="w-2.5 bg-amber-400 rounded-t-sm" style="height:88%"></div>
      </div>
      <span class="text-xs text-gray-500 text-center">Helpfulness</span>
    </div>
    <div class="flex-1 flex flex-col items-center gap-1">
      <div class="flex gap-0.5 items-end" style="height:48px">
        <div class="w-2.5 bg-indigo-600 rounded-t-sm" style="height:99%"></div>
        <div class="w-2.5 bg-emerald-500 rounded-t-sm" style="height:100%"></div>
        <div class="w-2.5 bg-amber-400 rounded-t-sm" style="height:97%"></div>
      </div>
      <span class="text-xs text-gray-500 text-center">Tone</span>
    </div>
  </div>
  <div class="flex gap-4 mt-2">
    <div class="flex items-center gap-1.5"><div class="w-3 h-2 rounded-sm bg-indigo-600"></div><span class="text-xs text-gray-500">gpt-4o-mini</span></div>
    <div class="flex items-center gap-1.5"><div class="w-3 h-2 rounded-sm bg-emerald-500"></div><span class="text-xs text-gray-500">o3-mini</span></div>
    <div class="flex items-center gap-1.5"><div class="w-3 h-2 rounded-sm bg-amber-400"></div><span class="text-xs text-gray-500">gpt-4o</span></div>
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

<div class="flex flex-col gap-5 mt-6">

<div v-click class="grid grid-cols-2 gap-5">
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

</div>

---
layout: center
class: text-center
---

<div class="flex flex-col items-center justify-center h-full gap-6">
  <div class="text-6xl font-bold text-gray-900">Thank you</div>
  <div class="text-xl text-gray-400">Questions?</div>
  <div class="mt-8 grid grid-cols-5 gap-6 max-w-4xl mx-auto">
    <div class="flex flex-col items-center gap-2.5">
      <img src="./images/team/raounek.png" class="w-20 h-20 rounded-full object-cover border-2 border-indigo-100 shadow-md" />
      <div>
        <div class="font-semibold text-gray-800 text-sm leading-tight">Raounek Zeghdoud</div>
        <div class="text-xs text-gray-400 mt-1">Mines Paris – PSL</div>
      </div>
    </div>
    <div class="flex flex-col items-center gap-2.5">
      <div class="w-20 h-20 rounded-full border-2 border-gray-200 shadow-md overflow-hidden flex-shrink-0">
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
    <div class="flex flex-col items-center gap-2.5">
      <img src="./images/team/solene.png" class="w-20 h-20 rounded-full object-cover border-2 border-indigo-100 shadow-md" />
      <div>
        <div class="font-semibold text-gray-800 text-sm leading-tight">Solène Delourme</div>
        <div class="text-xs text-gray-400 mt-1">CentraleSupélec</div>
      </div>
    </div>
    <div class="flex flex-col items-center gap-2.5">
      <img src="./images/team/antonio.png" class="w-20 h-20 rounded-full object-cover border-2 border-indigo-100 shadow-md" />
      <div>
        <div class="font-semibold text-gray-800 text-sm leading-tight">Antonio Zaitoun</div>
        <div class="text-xs text-gray-400 mt-1">University of Haifa</div>
      </div>
    </div>
    <div class="flex flex-col items-center gap-2.5">
      <img src="./images/team/donatas.png" class="w-20 h-20 rounded-full object-cover border-2 border-indigo-100 shadow-md" />
      <div>
        <div class="font-semibold text-gray-800 text-sm leading-tight">Donatas Iliška</div>
        <div class="text-xs text-gray-400 mt-1">Kaunas University of Technology</div>
      </div>
    </div>
  </div>
  <div class="mt-4 flex flex-col items-center gap-3">
    <img src="./images/QRCode.png" class="w-28 h-28" alt="QR code" />
    <a
      href="https://github.com/Minitour/customer-support-agent"
      target="_blank"
      rel="noopener noreferrer"
      class="text-sm text-indigo-600 hover:text-indigo-800 underline underline-offset-2"
    >
      github.com/Minitour/customer-support-agent
    </a>
  </div>
</div>
