
from typing import Any, Dict, Optional
from components.agents.base_agent import Agent
from components.agents.prompts import COMPLIANCE_VERIFIER_SYSTEM_PROMPT
from retreiver import retriever
from langchain_core.messages import SystemMessage, HumanMessage

class ComplianceVerifierAgent(Agent):
    """Agent responsible for verifying compliance of financial reports and documents."""
    
    def __init__(self):
        super().__init__(system_prompt=COMPLIANCE_VERIFIER_SYSTEM_PROMPT)
    
    def verify_compliance(self, document: str, standards_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Verify compliance of a financial report or document with AAOIFI standards.
        
        Args:
            document: The financial report or document to be verified
            standards_info: Optional information about relevant standards
            
        Returns:
            Dict with compliance verification results
        """
        # If we have standards info, include it as context
        standards_context = ""
        if standards_info:
            standards_context = f"\nPossibly Relevant Standards Information:\n{standards_info['extracted_info']}"
        print("Standards:", standards_context)
        print()
        # Use retriever to get additional relevant information
        retrieved_nodes = retriever.retrieve(document)
        additional_context = "\n\n".join([node.text for node in retrieved_nodes])
        
        # Prepare message for compliance verification
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Can you check compliance of this report with AAOIFI standards? Highlight flagged entries, violations, and suggestions in a clean table.
            
    Document:
    {document}

    {standards_context}
    Additional Context:
    {additional_context}
""")
        ]
        
        # Get compliance verification result
        response = self.llm.invoke(messages)
        
        return {
            "document": document,
            "compliance_report": response.content
        }