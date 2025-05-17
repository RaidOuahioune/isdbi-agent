def route_to_specialized_agent(query: str, llm) -> str:
    prompt = f"""
You are a system routing user queries to the most appropriate expert agent in an Islamic finance AI system.

Each agent handles a specific type of task:

### Challenge 1: Journal Entry Generator (Use Case Scenarios)
This agent receives detailed Islamic finance transaction scenarios (e.g., lease agreements, profit-sharing deals) and generates the correct journal entries in compliance with AAOIFI standards. It explains accounting treatments like asset recognition, amortization, or profit distribution.

Use this agent when the query contains narrative transaction descriptions needing accounting output.

---

### Challenge 2: Reverse Accounting Logic (Reverse Transactions)
This agent is given journal entries (without narrative context) and must reverse-engineer what kind of transaction occurred. It identifies the applicable AAOIFI standards and explains why.

Use this agent when the query involves unexplained or ambiguous journal entries and asks what they mean.

---

### Challenge 3: Compliance Checker
This agent scans financial reports or text documents for violations or inconsistencies with AAOIFI standards. It returns compliance analysis and flags issues.

Use this agent when the query asks whether a document or report is Shariah-compliant or adheres to AAOIFI standards.

---

### Challenge 4: Product Design Advisor
This agent helps users design new Islamic finance products. It recommends contract types (e.g., Murabaha, Musharaka), maps them to relevant FAS standards, and outlines Shariah concerns.

Use this agent when the user wants to build or evaluate a new Shariah-compliant financial product.

---

Given the user's query, return ONLY one of the following as your answer:
- "challenge_1"
- "challenge_2"
- "compliance_checker"
- "advisor"
- "none"

Do NOT explain your answer. Just return the agent name or "none".

### User Query:
{query}
""".strip()

    response = llm.complete(prompt)
    return response.text.strip().lower()
