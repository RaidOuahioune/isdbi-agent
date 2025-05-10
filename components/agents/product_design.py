"""
Product Design Advisor Agent for the Islamic Finance Standards System.

This agent helps users conceptualize new financial products based on their requirements,
ensuring alignment with AAOIFI standards and Shariah principles.
"""

from typing import Dict, Any, List, Optional
import logging
import sys
import re

# Import base agent class
from components.agents.base_agent import Agent
from components.agents.standards_extractor import standards_extractor
from retreiver import retriever
from langchain_core.messages import SystemMessage, HumanMessage

# Product design system prompt
PRODUCT_DESIGN_SYSTEM_PROMPT = """
You are an expert AI assistant specializing in the design of Shariah-compliant Islamic financial products. Your primary goal is to help users conceptualize new products based on their requirements, ensuring alignment with AAOIFI Financial Accounting Standards (FAS 4, 7, 10, 28, 32) and core Shariah principles.

Given user inputs detailing their product objectives, risk appetite, desired features, and target audience:
1. Analyze the requirements thoroughly.
2. Identify and recommend 1-2 suitable underlying Islamic contract structures (e.g., Mudarabah, Musharakah, Ijarah, Murabaha, Istisna'a, Salam, Wakalah). Provide a clear rationale for your selection, linking it back to the user's inputs.
3. For each recommended contract, outline a basic product structure (parties, flow, profit/loss sharing, ownership).
4. Crucially, consult with the 'StandardsExtractorAgent' (or use your retrieval tool) to identify and list key considerations and implications from the relevant AAOIFI FAS (specifically FAS 4, 7, 10, 28, and 32) that pertain to the proposed product concept. Focus on recognition, measurement, and disclosure aspects.
5. Consult with the 'ProductComplianceCheckAgent' (or use your Shariah validation tool) to provide initial Shariah compliance checkpoints. List critical Shariah principles (like avoiding Riba, Gharar, Maysir, ensuring asset-backing) that must be upheld for this product and highlight any potential areas of concern.
6. Briefly note any potential risks from an AAOIFI/Shariah compliance perspective and suggest high-level mitigation thoughts.
7. Suggest logical next steps for the user to take in the detailed design process.

Present your output in a clear, structured report format. Ensure your advice is practical and helps the user move towards a viable, compliant product concept. Do not invent new Shariah rules; base your compliance advice on established principles and AAOIFI guidelines.
"""

class ProductDesignAdvisorAgent(Agent):
    """Agent responsible for designing Shariah-compliant financial products."""

    def __init__(self):
        super().__init__(system_prompt=PRODUCT_DESIGN_SYSTEM_PROMPT)

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state and return a product design recommendation."""
        # Extract the relevant messages from the state
        messages = state.get("messages", [])
        # Get the product requirements from the state or from the last message
        product_requirements = state.get("product_requirements", {})
        
        # If product requirements are not in the state, use the last message
        if not product_requirements and messages:
            last_message = messages[-1]
            query = last_message.content if hasattr(last_message, "content") else ""
            # Extract requirements from the message
            product_requirements = self.extract_requirements_from_query(query)
        
        # Generate product design recommendation
        recommendation = self.design_product(product_requirements)
        
        # Create a new state with the recommendation
        new_state = state.copy()
        new_state["product_design"] = recommendation
        
        return new_state
    
    def extract_requirements_from_query(self, query: str) -> Dict[str, Any]:
        """Extract product requirements from a natural language query."""
        # This is a simple implementation - could be enhanced with a more sophisticated approach
        requirements = {
            "product_objective": "",
            "risk_appetite": "",
            "investment_tenor": "",
            "target_audience": "", 
            "asset_focus": "",
            "desired_features": [],
            "specific_exclusions": []
        }
        
        # Use the LLM to extract structured requirements from the query
        extract_prompt = f"""
        Extract key product design requirements from the following query:
        
        {query}
        
        Extract and format the following information:
        - Product Objective: [The main goal of the product]
        - Risk Appetite: [Low/Medium/High]
        - Investment Tenor: [Short-term/Medium-term/Long-term]
        - Target Audience: [Retail/Corporate/HNWI/etc.]
        - Asset Focus: [Real estate/Commodities/Equity/etc. or None if not specified]
        - Desired Features: [List of desired features]
        - Specific Exclusions: [List of things to avoid]
        
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
                # Update requirements with extracted values
                for key in requirements:
                    if key in extracted_json:
                        requirements[key] = extracted_json[key]
        except Exception as e:
            logging.error(f"Error extracting requirements: {e}")
            
        return requirements
    
    def design_product(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design a product based on the provided requirements.
        This is the main method that implements the product design logic.
        """
        # Format the requirements for the prompt
        requirements_text = "\n".join([
            f"- {key.replace('_', ' ').title()}: {value if isinstance(value, str) else ', '.join(value)}"
            for key, value in requirements.items() if value
        ])
        
        # Step 1: Identify suitable Islamic contracts
        contract_prompt = f"""
        Based on the following product requirements, identify 1-2 most suitable Islamic contracts
        and provide a detailed rationale for your selection:
        
        {requirements_text}
        
        Format your response as:
        RECOMMENDED_CONTRACTS: [comma-separated list of contracts]
        RATIONALE: [your detailed explanation]
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=contract_prompt)
        ]
        
        contract_response = self.llm.invoke(messages)
        
        # Parse the contract response
        recommended_contracts = []
        rationale = ""
        
        contracts_match = re.search(r'RECOMMENDED_CONTRACTS:\s*(.*?)(?:\n|$)', contract_response.content)
        if contracts_match:
            contracts_text = contracts_match.group(1).strip("[] ")
            recommended_contracts = [c.strip() for c in contracts_text.split(',')]
        
        rationale_match = re.search(r'RATIONALE:\s*(.*?)(?:\n\n|$)', contract_response.content, re.DOTALL)
        if rationale_match:
            rationale = rationale_match.group(1).strip()
            
        # Step 2: Get information about relevant standards for the recommended contracts
        standards_info = {}
        for contract in recommended_contracts:
            # Determine which standards are relevant for this contract
            relevant_standards = self.get_relevant_standards_for_contract(contract)
            
            # Query the standards extractor for each relevant standard
            for std_id in relevant_standards:
                query = f"Key requirements and considerations from FAS {std_id} for a {contract} product for {requirements.get('product_objective', 'investment')}."
                result = standards_extractor.extract_standard_info(std_id, query)
                
                if std_id not in standards_info:
                    standards_info[std_id] = result
        
        # Step 3: Generate the product structure
        structure_prompt = f"""
        Create a detailed product structure for a {', '.join(recommended_contracts)} based product with these requirements:
        
        {requirements_text}
        
        Your response should follow this structure:
        PRODUCT_STRUCTURE:
        1. Parties and Roles:
        [list parties and their roles]
        
        2. Flow of Funds/Assets:
        [describe the flow]
        
        3. Profit/Loss Mechanism:
        [explain mechanism]
        
        4. Ownership Structure:
        [explain ownership]
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=structure_prompt)
        ]
        
        structure_response = self.llm.invoke(messages)
        
        # Step 4: Generate compliance checkpoints using Shariah principles knowledge
        from shariah_principles import format_principles_for_validation
        
        # Get principles for all relevant standards
        principles_text = ""
        for std_id in standards_info.keys():
            principles_text += format_principles_for_validation(std_id) + "\n\n"
        
        compliance_prompt = f"""
        Based on the following product concept and Shariah principles, identify key compliance checkpoints, 
        potential concerns, and risk mitigation strategies:
        
        PRODUCT CONCEPT:
        - Contracts: {', '.join(recommended_contracts)}
        - Objective: {requirements.get('product_objective', '')}
        - Features: {', '.join(requirements.get('desired_features', []))}
        
        PRODUCT STRUCTURE:
        {structure_response.content}
        
        SHARIAH PRINCIPLES:
        {principles_text}
        
        Provide your assessment in this format:
        
        COMPLIANCE_CHECKPOINTS:
        - [list 3-5 key compliance checkpoints]
        
        POTENTIAL_CONCERNS:
        - [list any potential Shariah concerns]
        
        RISK_MITIGATION:
        [brief notes on mitigating Shariah compliance risks]
        
        NEXT_STEPS:
        - [recommend 3-4 concrete next steps for ensuring Shariah compliance]
        """
        
        messages = [
            SystemMessage(content="You are a Shariah compliance expert."),
            HumanMessage(content=compliance_prompt)
        ]
        
        compliance_response = self.llm.invoke(messages)
        
        # Parse compliance response
        compliance_checkpoints = []
        potential_concerns = []
        risk_mitigation = ""
        next_steps = []
        
        checkpoints_match = re.search(r'COMPLIANCE_CHECKPOINTS:(.*?)(?:POTENTIAL_CONCERNS:|$)', 
                                     compliance_response.content, re.DOTALL)
        if checkpoints_match:
            checkpoints_text = checkpoints_match.group(1).strip()
            compliance_checkpoints = [line.strip('- ').strip() for line in checkpoints_text.split('\n') 
                                    if line.strip() and line.strip().startswith('-')]
        
        concerns_match = re.search(r'POTENTIAL_CONCERNS:(.*?)(?:RISK_MITIGATION:|$)', 
                                 compliance_response.content, re.DOTALL)
        if concerns_match:
            concerns_text = concerns_match.group(1).strip()
            potential_concerns = [line.strip('- ').strip() for line in concerns_text.split('\n') 
                                if line.strip() and line.strip().startswith('-')]
        
        mitigation_match = re.search(r'RISK_MITIGATION:(.*?)(?:NEXT_STEPS:|$)', 
                                   compliance_response.content, re.DOTALL)
        if mitigation_match:
            risk_mitigation = mitigation_match.group(1).strip()
        
        steps_match = re.search(r'NEXT_STEPS:(.*?)(?:$)', compliance_response.content, re.DOTALL)
        if steps_match:
            steps_text = steps_match.group(1).strip()
            next_steps = [line.strip('- ').strip() for line in steps_text.split('\n') 
                        if line.strip() and line.strip().startswith('-')]
        
        # Step 5: Generate a creative product name
        name_prompt = f"""
        Suggest a creative but professional name for an Islamic finance product with these characteristics:
        - Based on {', '.join(recommended_contracts)} contract(s)
        - For {requirements.get('product_objective', 'investment')}
        - Targeting {requirements.get('target_audience', 'investors')}
        
        Return only the name, without explanation.
        """
        
        messages = [
            SystemMessage(content="You are a creative product naming specialist."),
            HumanMessage(content=name_prompt)
        ]
        
        name_response = self.llm.invoke(messages)
        suggested_name = name_response.content.strip()
        
        # Compile the final product design recommendation
        product_design = {
            "suggested_product_concept_name": suggested_name,
            "recommended_islamic_contracts": recommended_contracts,
            "rationale_for_contract_selection": rationale,
            "proposed_product_structure_overview": structure_response.content,
            "key_aaoifi_fas_considerations": standards_info,
            "shariah_compliance_checkpoints": compliance_checkpoints,
            "potential_areas_of_concern": potential_concerns,
            "potential_risks_and_mitigation_notes": risk_mitigation,
            "next_steps_for_detailed_design": next_steps,
            "original_requirements": requirements
        }
        
        return product_design
    
    def get_relevant_standards_for_contract(self, contract: str) -> List[str]:
        """Determine which AAOIFI standards are most relevant for a given contract type."""
        contract_to_standards = {
            "Mudarabah": ["4"],
            "Musharakah": ["4"],
            "Diminishing Musharakah": ["4"],
            "Ijarah": ["32"],
            "Ijarah Muntahia Bittamleek": ["32"],
            "Murabaha": ["28"],
            "Istisna'a": ["10"],
            "Parallel Istisna'a": ["10"],
            "Salam": ["7"],
            "Parallel Salam": ["7"],
            "Wakalah": ["4", "32"], # Often used in conjunction with others
            "Sukuk": ["32", "4", "10"] # Depends on underlying structure
        }
        
        # Default to standards 28 and 4 if contract not found
        return contract_to_standards.get(contract, ["28", "4"])


# Initialize the agent
product_design_advisor = ProductDesignAdvisorAgent() 