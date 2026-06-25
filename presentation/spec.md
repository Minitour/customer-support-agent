## Presentation Layout

Problem -> Approach -> Architecture -> Evaluation -> Limitations -> Next Steps


### Problem
Customers often need to contact support by 
email or phone for simple questions about their
orders or website policies. This agent can 
automatically answer these common questions,
providing faster support to customers while 
reducing the workload of the support team.

### Approach
Website + Customer support agent integrated

One LLM-based Agent
- OpenAI gpt-4o-mini
- Ollama : Qwen coder Instruct

Tools
- search_policy(query)
- search_product(query)
- get_order_status(order_id)
- get_order_history(user_id)

Knowledge Database
- ChromaDB
- Embedding model : text-embedding-3-small
- Policy files in Markdown  

SQL Database
- Postgres 
- Product files in json
- Order files in ...
- 3 tables : Products, Orders, Users


### Evaluation
Exectution : is the agent call right tools ? (determinictic evaluation) 
Quality : is the response is expected ? (how can we evaluate ? 
Human validation ? LLM-as-a-Judge ? )

20 tests 

get_policy(query)
1.
2.

get_product(query)
1.
2.

get_order_status(order_id)
1.
2.

get_order_history(user_id)
1.
2.

Multi tools questions
1. 
2.
3.
4.

No information 
1.
2.

Human actions 
1.
2.


### Limitations
FIRST PROPOSITION

LLM 
1. If we use a closed model as OpenAI model, the limitations can be the cost. Each token has
a price 
-> replace it with an open-source model can resolve the problem but increase other risks.

Security
Depend on the model, it important to verify that the model is not jailbreaking and do not 
give personal information. 


## Images
- /images/system-architecture-white-background.png

## The Team
- Raounek Zeghdoud (PhD Student at Mines Paris - PSL)
- Nada Alrehaili (PhD Student at University of Liverpool)
- Solene Delourme (PhD Student at CentraleSupélec)
- Antonio Zaitoun (PhD Student at University of Haifa)
- Donatas Iliška (PhD Student at Kaunas University of Technology)