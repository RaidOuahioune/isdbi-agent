# filepath: c:\Users\ELITE COMPUTER\Desktop\Hackaton\isdbi\isdbi-agent\components\agents\transaction_rationale.py
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, Union
from components.agents.base_agent import Agent
from components.agents.prompts import TRANSACTION_RATIONALE_SYSTEM_PROMPT
from retreiver import retriever
import logging
import re


class TransactionStandardRationaleAgent(Agent):
    """Agent responsible for explaining why a specific standard applies to a transaction."""

    def __init__(self):
        super().__init__(system_prompt=TRANSACTION_RATIONALE_SYSTEM_PROMPT)

    def _generate_references_section(self, rationale, references, referenced_sections):
        """
        Generate a "References" section to be appended to the rationale if one doesn't exist.

        Args:
            rationale: The original rationale text
            references: List of reference markers
            referenced_sections: Dict mapping references to their text content

        Returns:
            Updated rationale text with references section
        """
        # Check if a references section already exists
        if "References" in rationale and any(
            ref in rationale.split("References")[1] for ref in references
        ):
            return rationale

        # Create a references section
        references_section = "\n\n## References\n\n"
        for i, ref in enumerate(references):
            ref_content = referenced_sections.get(ref, "").strip()
            # Limit the content length for readability
            if len(ref_content) > 200:
                ref_content = ref_content[:197] + "..."

            references_section += f"{i + 1}. {ref}: {ref_content}\n\n"

        return rationale + references_section

    def _extract_referenced_sections(self, standard_text, references):
        """
        Extract sections of the standard text that correspond to specific references.

        Args:
            standard_text: The full text of the standard
            references: List of reference markers like [Section X.XX]

        Returns:
            Dict mapping reference markers to the corresponding text sections
        """
        referenced_sections = {}

        for ref in references:
            # Extract the reference identifier without brackets
            ref_clean = ref.strip("[]")

            # Create a pattern to potentially find this section in the text
            # This is a simple heuristic - might need refinement based on actual standards format
            pattern = re.compile(
                f"{ref_clean}[:\.\s]+(.*?)(?=(?:Section|Paragraph|Clause|Part)|\Z)",
                re.DOTALL | re.IGNORECASE,
            )

            matches = pattern.findall(standard_text)
            if matches:
                referenced_sections[ref] = matches[0].strip()
            else:
                referenced_sections[ref] = (
                    "Section text could not be automatically extracted"
                )

        return referenced_sections

    def explain_standard_application(
        self, transaction_input: Union[str, Dict[str, Any]], standard_id: str
    ) -> Dict[str, Any]:
        """
        Explain why a specific standard applies to a transaction.

        Args:
            transaction_input: Either a string describing the transaction or a Dict
                          containing transaction details
            standard_id: The ID of the standard to explain (e.g., "FAS 4")

        Returns:
            Dict containing rationale explanation
        """
        # Handle string input vs. dictionary input
        if isinstance(transaction_input, str):
            transaction_details = {"context": transaction_input}
            transaction_query = transaction_input
        else:
            # Format transaction details by leveraging the TransactionAnalyzerAgent method
            transaction_details = transaction_input
            from components.agents.transaction_analyzer import transaction_analyzer

            transaction_query = transaction_analyzer._build_structured_query(
                transaction_details
            )

        # Get specific information about the standard
        standard_query = f"Detailed information about {standard_id} including scope, recognition criteria, and measurement requirements"
        retrieved_nodes = retriever.retrieve(standard_query)

        # Log retrieved chunks
        logging.info(
            f"RationaleAgent: Retrieved {len(retrieved_nodes)} chunks for standard {standard_id}"
        )
        for i, node in enumerate(retrieved_nodes[:2]):
            logging.info(f"Standard chunk {i + 1}: {node.text[:100]}...")

        standard_info = "\n\n".join(
            [node.text for node in retrieved_nodes]
        )  # Prepare message for rationale explanation
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please explain in detail why {standard_id} applies to this transaction:
            
Transaction:
{transaction_query}

Standard Information:
{standard_info}

Provide a comprehensive explanation addressing:
1. Transaction Analysis: Identify key elements of the transaction related to {standard_id}
2. Standard Requirements: Outline the specific requirements of {standard_id} that apply
3. Matching Rationale: Explain how transaction elements match standard requirements
4. Evidence-Based Reasoning: Cite specific clauses of {standard_id} supporting this application
5. Confidence Level: Assess how confident you are that this standard applies (high/medium/low)


At the end of your explanation, include a "References" section that lists all the cited sections, paragraphs, 
and clauses in an organized manner with brief descriptions of what each reference covers.
            """
            ),
        ]  # Get response from the model
        response = self.llm.invoke(messages)
        # Extract references from the response
        # This will look for patterns like [Section X.XX], [Paragraph Y], etc.
        references = re.findall(
            r"\[(Section|Paragraph|Clause|Part)[\s\w\d\.\-]+\]", response.content
        )

        # Remove duplicates while preserving order
        unique_references = []
        for ref in references:
            if ref not in unique_references:
                unique_references.append(ref)
        # Extract the actual text for each reference
        referenced_sections = self._extract_referenced_sections(
            standard_info, unique_references
        )

        # Log the references found
        logging.info(
            f"RationaleAgent: Found {len(unique_references)} unique references to {standard_id}"
        )
        for ref in unique_references[:3]:  # Log first few references
            logging.info(f"Reference: {ref}")

        # Ensure the rationale has a References section at the end
        enhanced_rationale = self._generate_references_section(
            response.content, unique_references, referenced_sections
        )

        return {
            "standard_id": standard_id,
            "transaction_details": transaction_details,
            "rationale": enhanced_rationale,
            "references": unique_references,
            "referenced_sections": referenced_sections,
        }


# Initialize the agent
transaction_rationale = TransactionStandardRationaleAgent()
