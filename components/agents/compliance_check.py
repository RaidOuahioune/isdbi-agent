"""
Product Compliance Check Agent for the Islamic Finance Standards System.

This agent evaluates Shariah compliance for financial product concepts,
providing preliminary assessments based on core Shariah principles and AAOIFI guidelines.
"""

from typing import Dict, Any, List, Optional
import logging
import sys
import re

# Import base agent class
from components.agents.base_agent import Agent
from langchain_core.messages import SystemMessage, HumanMessage
from shariah_principles import format_principles_for_validation, get_principles_for_standard

# Compliance checker system prompt
COMPLIANCE_CHECK_SYSTEM_PROMPT = """
You are an AI Shariah Compliance Checker for new Islamic financial product concepts. Your role is to provide a preliminary assessment based on core Shariah principles and general AAOIFI guidelines.

Given a conceptual product structure (including the proposed Islamic contract(s) and key features):
1. Analyze the concept against fundamental Shariah principles:
   * Prohibition of Riba (Interest).
   * Prohibition of Gharar (Excessive Uncertainty).
   * Prohibition of Maysir (Gambling).
   * Requirement of Asset-Backing (where applicable).
   * Principles of Risk-Sharing and Justice.
   * Avoidance of prohibited (Haram) activities or assets.
2. Identify which of these principles are most critical to address for the given product concept.
3. Highlight any potential features or structures in the concept that might raise Shariah concerns or require careful structuring to ensure compliance.
4. Refer to the provided list of Shariah principles and relevant AAOIFI FAS (4, 7, 10, 28, 32) general guidelines when formulating your advice.
5. Output a list of "Shariah Compliance Checkpoints" and "Potential Areas of Concern."

Your assessment is preliminary and for guidance only. The user must consult with qualified Shariah scholars for formal approval. Do not provide a definitive fatwa.
"""

class ProductComplianceCheckAgent(Agent):
    """Agent responsible for evaluating Shariah compliance of financial product concepts."""

    def __init__(self):
        super().__init__(system_prompt=COMPLIANCE_CHECK_SYSTEM_PROMPT)

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state and return a compliance assessment."""
        # Extract the product concept from the state
        product_concept = state.get("product_concept", {})
        
        # If no product concept in state, check if it's in the product design
        if not product_concept and "product_design" in state:
            product_design = state.get("product_design", {})
            product_concept = {
                "name": product_design.get("suggested_product_concept_name", ""),
                "contracts": product_design.get("recommended_islamic_contracts", []),
                "structure": product_design.get("proposed_product_structure_overview", ""),
                "requirements": product_design.get("original_requirements", {})
            }
        
        # If still no product concept, check the last message
        if not product_concept and "messages" in state:
            messages = state.get("messages", [])
            if messages:
                last_message = messages[-1]
                query = last_message.content if hasattr(last_message, "content") else ""
                # Extract a basic product concept from the message
                product_concept = self.extract_concept_from_query(query)
        
        # Perform compliance check
        compliance_assessment = self.check_compliance(product_concept)
        
        # Create a new state with the compliance assessment
        new_state = state.copy()
        new_state["compliance_assessment"] = compliance_assessment
        
        return new_state
    
    def extract_concept_from_query(self, query: str) -> Dict[str, Any]:
        """Extract a basic product concept from a natural language query."""
        # This is a simple implementation - could be enhanced with a more sophisticated approach
        concept = {
            "name": "",
            "contracts": [],
            "structure": "",
            "requirements": {}
        }
        
        # Use the LLM to extract a basic product concept
        extract_prompt = f"""
        Extract key information about an Islamic financial product concept from the following query:
        
        {query}
        
        Extract and format the following information:
        - Product Name: [Name of the product or concept]
        - Islamic Contracts: [List of Islamic contracts mentioned]
        - Product Structure: [Any details about the structure]
        - Requirements: [Any requirements or features mentioned]
        
        Format your answer as a JSON object with these exact keys. If any information is not provided, leave the value empty.
        """
        
        messages = [
            SystemMessage(content="You are a helpful assistant that extracts structured information from text."),
            HumanMessage(content=extract_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Extract JSON from the response
        try:
            # Find JSON-like structure in the response
            json_match = re.search(r'({[\s\S]*})', response.content)
            if json_match:
                import json
                extracted_json = json.loads(json_match.group(1))
                # Update concept with extracted values
                for key in concept:
                    if key in extracted_json:
                        concept[key] = extracted_json[key]
        except Exception as e:
            logging.error(f"Error extracting product concept: {e}")
            
        return concept
    
    def check_compliance(self, product_concept: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the Shariah compliance of a product concept.
        
        Args:
            product_concept: Dictionary containing product concept details
            
        Returns:
            Dictionary with compliance assessment results
        """
        # Extract relevant information from the product concept
        product_name = product_concept.get("name", "")
        contracts = product_concept.get("contracts", [])
        structure = product_concept.get("structure", "")
        requirements = product_concept.get("requirements", {})
        
        # If no contracts specified, try to infer from the structure or name
        if not contracts:
            # Simple keyword matching - could be enhanced with more sophisticated NLP
            common_contracts = [
                "Mudarabah", "Musharakah", "Ijarah", "Murabaha", "Istisna'a", 
                "Salam", "Wakalah", "Sukuk", "Takaful"
            ]
            
            for contract in common_contracts:
                if contract.lower() in structure.lower() or contract.lower() in product_name.lower():
                    contracts.append(contract)
        
        # Get relevant standards for the contracts
        relevant_standards = []
        for contract in contracts:
            # Map contracts to standards - this is a simplified version
            if contract in ["Mudarabah", "Musharakah"]:
                relevant_standards.append("4")
            elif contract in ["Salam", "Parallel Salam"]:
                relevant_standards.append("7")
            elif contract in ["Istisna'a", "Parallel Istisna'a"]:
                relevant_standards.append("10")
            elif contract in ["Murabaha"]:
                relevant_standards.append("28")
            elif contract in ["Ijarah", "Ijarah Muntahia Bittamleek"]:
                relevant_standards.append("32")
        
        # Remove duplicates
        relevant_standards = list(set(relevant_standards))
        
        # Default to standard 4 if no relevant standards found
        if not relevant_standards:
            relevant_standards = ["4"]
        
        # Get principles for all relevant standards
        principles_text = ""
        for std_id in relevant_standards:
            principles_text += format_principles_for_validation(std_id) + "\n\n"
        
        # Format the product concept for the compliance check
        product_description = f"""
        Product Name: {product_name}
        Islamic Contracts: {', '.join(contracts)}
        
        Product Structure:
        {structure}
        
        Requirements:
        {str(requirements)}
        """
        
        # Create the compliance check prompt
        compliance_prompt = f"""
        Perform a Shariah compliance check on the following Islamic financial product concept:
        
        {product_description}
        
        Based on these Shariah principles:
        
        {principles_text}
        
        Provide your assessment in this format:
        
        COMPLIANCE_CHECKPOINTS:
        - [List 3-5 key compliance checkpoints]
        
        POTENTIAL_CONCERNS:
        - [List any potential Shariah concerns]
        
        RISK_MITIGATION:
        [Brief notes on mitigating Shariah compliance risks]
        
        NEXT_STEPS:
        - [Recommend 3-4 concrete next steps for ensuring Shariah compliance]
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=compliance_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse the response to extract structured information
        compliance_checkpoints = []
        potential_concerns = []
        risk_mitigation = ""
        next_steps = []
        
        # Extract compliance checkpoints
        checkpoints_match = re.search(r'COMPLIANCE_CHECKPOINTS:(.*?)(?:POTENTIAL_CONCERNS:|$)', 
                                    response.content, re.DOTALL)
        if checkpoints_match:
            checkpoints_text = checkpoints_match.group(1).strip()
            compliance_checkpoints = [line.strip('- ').strip() for line in checkpoints_text.split('\n') 
                                    if line.strip() and line.strip().startswith('-')]
        
        # Extract potential concerns
        concerns_match = re.search(r'POTENTIAL_CONCERNS:(.*?)(?:RISK_MITIGATION:|$)', 
                                 response.content, re.DOTALL)
        if concerns_match:
            concerns_text = concerns_match.group(1).strip()
            potential_concerns = [line.strip('- ').strip() for line in concerns_text.split('\n') 
                                if line.strip() and line.strip().startswith('-')]
        
        # Extract risk mitigation
        mitigation_match = re.search(r'RISK_MITIGATION:(.*?)(?:NEXT_STEPS:|$)', 
                                   response.content, re.DOTALL)
        if mitigation_match:
            risk_mitigation = mitigation_match.group(1).strip()
        
        # Extract next steps
        steps_match = re.search(r'NEXT_STEPS:(.*?)(?:$)', response.content, re.DOTALL)
        if steps_match:
            steps_text = steps_match.group(1).strip()
            next_steps = [line.strip('- ').strip() for line in steps_text.split('\n') 
                        if line.strip() and line.strip().startswith('-')]
        
        # Compile the compliance assessment
        compliance_assessment = {
            "compliance_checkpoints": compliance_checkpoints,
            "potential_concerns": potential_concerns,
            "risk_mitigation": risk_mitigation,
            "next_steps": next_steps,
            "relevant_standards": relevant_standards
        }
        
        return compliance_assessment


# Initialize the agent
product_compliance_checker = ProductComplianceCheckAgent() 