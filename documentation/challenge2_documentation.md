# Islamic Finance Category 2: Reverse Transactions Agent System

This document provides a detailed breakdown of how the specialized agents work together to process Category 2 (Reverse Transactions) scenarios in the ISDBI Agent system for Islamic finance standards.

## Overview

Category 2 (Reverse Transactions) in the Islamic finance system involves analyzing journal entries from existing transactions to identify which AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions) Financial Accounting Standards (FAS) are most applicable. This category employs three specialized agents working together in a sequential workflow:

1. **Transaction Analyzer Agent**
2. **Transaction Rationale Agent**
3. **Knowledge Integration Agent**

## Agent Architecture

### Transaction Analyzer Agent

**Purpose**: Analyzes journal entries and transaction details to identify applicable AAOIFI standards.

**Key Features**:
- Processes structured financial transaction data
- Uses RAG (Retrieval-Augmented Generation) to reference relevant standards
- Ranks standards by probability of applicability
- Provides detailed reasoning for each identified standard

**Implementation Details**:
```python
class TransactionAnalyzerAgent(Agent):
    """Agent responsible for analyzing journal entries to identify applicable AAOIFI standards."""

    def __init__(self):
        super().__init__(system_prompt=TRANSACTION_ANALYZER_SYSTEM_PROMPT)
        self.retriever = retriever  # Vector database retriever

    def analyze_transaction(self, transaction_details: Dict[str, Any]) -> Dict[str, Any]:
        # Build structured query from transaction details
        query = self._build_structured_query(transaction_details)
        
        # Retrieve relevant standards information
        retrieved_nodes = self.retriever.retrieve(query)
        standards_context = "\n\n".join([node.text for node in retrieved_nodes])
        
        # Generate analysis with LLM
        response = self.llm.invoke(messages)
        
        # Extract standards mentioned in response
        standards = self._extract_standards(response.content)
        
        return {
            "transaction_details": transaction_details,
            "analysis": response.content,
            "identified_standards": standards,
            "retrieval_stats": {...}
        }
```

**System Prompt Focus**:
- Focus on reverse transactions (unwound, cancelled, or reversed transactions)
- Rank standards by probability when multiple apply
- Structure analysis with transaction summary and detailed reasoning
- Restrict analysis to FAS 4, 7, 10, 28, and 32
- Only consider information explicitly provided in transaction details

### Transaction Rationale Agent

**Purpose**: Provides detailed explanations for why specific standards apply to a transaction.

**Key Features**:
- Works with a single standard at a time
- Retrieves detailed information about the specific standard
- Provides evidence-based reasoning with citations to specific clauses
- Assesses confidence level for standard applicability

**Implementation Details**:
```python
class TransactionStandardRationaleAgent(Agent):
    """Agent responsible for explaining why a specific standard applies to a transaction."""

    def explain_standard_application(
        self, transaction_details: Dict[str, Any], standard_id: str
    ) -> Dict[str, Any]:
        # Format transaction details
        transaction_query = transaction_analyzer._build_structured_query(transaction_details)
        
        # Get specific information about the standard
        standard_query = f"Detailed information about {standard_id}..."
        retrieved_nodes = retriever.retrieve(standard_query)
        standard_info = "\n\n".join([node.text for node in retrieved_nodes])
        
        # Generate detailed explanation with LLM
        response = self.llm.invoke(messages)
        
        return {
            "standard_id": standard_id,
            "transaction_details": transaction_details,
            "rationale": response.content,
        }
```

**System Prompt Focus**:
- Provide evidence-based reasoning connecting transaction elements to standard requirements
- Cite specific clauses or sections of standards
- Include transaction analysis, standard requirements, matching rationale
- Assess confidence level (high/medium/low) with justification
- Restrict analysis to explicitly mentioned elements in transaction context

### Knowledge Integration Agent

**Purpose**: Integrates transaction analysis with standards knowledge to provide a comprehensive final assessment.

**Key Features**:
- Combines outputs from previous agents
- Resolves conflicts between potentially applicable standards
- Prioritizes the most relevant standards
- Provides comprehensive accounting treatment recommendations
- Highlights special considerations for transaction types

**Implementation Details**:
```python
class KnowledgeIntegrationAgent(Agent):
    """Agent responsible for integrating transaction analysis with standards knowledge."""

    def integrate_knowledge(
        self, transaction_analysis: Dict[str, Any], standard_rationales: Dict[str, str]
    ) -> Dict[str, Any]:
        # Format the transaction analysis
        transaction_str = json.dumps(transaction_analysis["transaction_details"], indent=2)
        analysis_str = transaction_analysis["analysis"]
        
        # Format the standard rationales
        rationales_str = ""
        for std_id, rationale in standard_rationales.items():
            rationales_str += f"\n\n--- {std_id} RATIONALE ---\n{rationale}"
        
        # Generate integrated analysis with LLM
        response = self.llm.invoke(messages)
        
        return {
            "transaction_analysis": transaction_analysis,
            "standard_rationales": standard_rationales,
            "integrated_analysis": response.content,
        }
```

**System Prompt Focus**:
- Connect transaction patterns with standards content
- Resolve conflicts between multiple applicable standards
- Prioritize based on transaction specifics and standard scope
- Provide integrated view showing how standards apply to transactions
- Base analysis exclusively on provided transaction context

## Workflow Process

The Category 2 workflow follows these steps:

1. **Initial Analysis**:
   - Transaction details (context, journal entries, additional info) are received
   - Transaction Analyzer Agent processes the structured data
   - RAG retrieval finds relevant standard information
   - Agent ranks applicable standards with probabilities and reasoning
   - Returns analysis and identified standards

2. **Standard Rationale Analysis**:
   - For top identified standards (usually top 2 for efficiency)
   - Transaction Rationale Agent provides detailed explanation for each standard
   - Cites specific clauses and requirements from standards
   - Returns detailed rationales for each standard

3. **Knowledge Integration**:
   - Combines transaction analysis and standard rationales
   - Knowledge Integration Agent resolves conflicts between standards
   - Prioritizes most applicable standards
   - Provides final comprehensive accounting treatment
   - Returns integrated analysis with final recommendations

4. **Final Response**:
   - Integrated analysis is presented to the user
   - Contains ranked standards with justifications
   - Provides accounting guidance based on most applicable standards
   - Includes specific citations to relevant standards sections

## Example Use Cases

1. **Partner Equity Buyout**:
   - Transaction involves buyout of a partner's stake
   - System identifies FAS 4 (Mudarabah) as primary standard
   - May also identify FAS 7 (Musharakah) with lower probability

2. **Contract Change Order Reversal**:
   - Transaction involves reverting to original contract terms
   - System identifies FAS 10 (Istisna'a) as primary standard
   - Explains how the reversal should be treated under the standard

3. **Sukuk Early Termination**:
   - Transaction involves early cancellation of Islamic bonds
   - System identifies applicable standards and explains accounting treatment
   - Provides detailed justification for recommended accounting approach

## Key Strengths

1. **Evidence-Based Reasoning**: All recommendations are backed by specific clauses and requirements from AAOIFI standards.

2. **Comprehensive Analysis**: The multi-agent approach ensures thorough analysis from multiple perspectives.

3. **Conflict Resolution**: The system can handle cases where multiple standards could apply and provide reasoned prioritization.

4. **Strict Adherence to Standards**: The system focuses exclusively on the five key standards (FAS 4, 7, 10, 28, 32) and does not introduce information beyond transaction context.

5. **RAG-Enhanced Responses**: Vector database retrieval ensures recommendations are based on accurate standard information rather than hallucinated content.
