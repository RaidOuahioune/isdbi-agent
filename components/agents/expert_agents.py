
import logging
from typing import Dict, Any, List, Optional, Tuple

from langchain_core.messages import SystemMessage, HumanMessage
from sklearn.feature_extraction.text import TfidfVectorizer

# Assuming 'retriever' is an instance of a retriever class, correctly imported
from retreiver import retriever # If your module is 'retreiver', this is correct.

# Import base agent class (ensure this path is correct for your project)
from components.agents.base_agent import Agent

# Domain-specific keywords (ensure this path or definition is correct)
from components.evaluation.utils import DOMAIN_KEYWORDS_FIXED

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- New System Prompts for Proposal Analysis ---
# These prompts guide the experts to analyze proposals using retrieved context.

BASE_EXPERT_SYSTEM_PROMPT_TEMPLATE = """
You are an expert in {expertise_area}.
Your task is to analyze a proposed enhancement to an AAOIFI standard from your domain perspective.
Carefully review the provided:
1. The Enhancement Proposal itself.
2. The history of Previous Discussions regarding this proposal.
3. Relevant Excerpts from existing AAOIFI standards that have been retrieved for context.

Based on all this information, provide your expert opinion.

Structure your response strictly as follows:
ANALYSIS:
(Your detailed analysis, integrating insights from the proposal, discussion, and retrieved standards. Be specific and justify your points by referencing these materials.)

CONCERNS:
1. (List your primary concern related to your domain. Be specific and explain why it's a concern, linking it to the proposal or standards. If no major concerns, state "None.")
2. (List your secondary concern, if any.)

RECOMMENDATIONS:
1. (Suggest a specific, actionable recommendation to address a concern or improve the proposal from your domain perspective. If no specific recommendations, state "None.")
2. (Suggest another recommendation, if applicable.)

Focus on critical issues. Be clear, concise, and constructive.
Your analysis should demonstrate a thorough understanding of your domain and the provided materials.
"""

SHARIAH_EXPERT_PROPOSAL_PROMPT = BASE_EXPERT_SYSTEM_PROMPT_TEMPLATE.format(expertise_area="Shariah and Islamic Finance Principles") + """
Specifically, from a Shariah compliance perspective, consider:
- Adherence to core Islamic finance principles (e.g., avoidance of Riba, Gharar, Maysir).
- Alignment with the Maqasid al-Shari'ah (objectives of Shariah).
- Potential impact on contract validity and enforceability.
- Clarity and unambiguity of Shariah guidance in the proposal.
- Consistency with established Shariah rulings and interpretations within AAOIFI's framework.
"""

FINANCE_EXPERT_PROPOSAL_PROMPT = BASE_EXPERT_SYSTEM_PROMPT_TEMPLATE.format(expertise_area="Islamic Financial Accounting and Reporting") + """
Specifically, from a financial accounting and reporting perspective, consider:
- Recognition, measurement, and derecognition implications.
- Presentation and disclosure requirements in financial statements.
- Impact on financial ratios and analysis.
- Practicality of accounting procedures and systems needed.
- Consistency with the AAOIFI conceptual framework and existing FAS.
"""

STANDARDS_EXPERT_PROPOSAL_PROMPT = BASE_EXPERT_SYSTEM_PROMPT_TEMPLATE.format(expertise_area="AAOIFI Standards Structure, Consistency, and Clarity") + """
Specifically, from a standards coherence perspective, consider:
- Clarity, precision, and unambiguity of the proposed wording.
- Consistency with other AAOIFI standards (Shariah, Accounting, Governance, Ethics).
- Potential for misinterpretation or conflicting application.
- Completeness of the proposal in addressing the identified issue.
- Logical flow and structure of the proposed text.
"""

PRACTICAL_EXPERT_PROPOSAL_PROMPT = BASE_EXPERT_SYSTEM_PROMPT_TEMPLATE.format(expertise_area="Practical Implementation and Industry Application of Islamic Finance Standards") + """
Specifically, from a practical implementation perspective, consider:
- Operational feasibility for Islamic financial institutions.
- Impact on existing products, processes, and systems.
- Training and resource requirements for implementation.
- Potential challenges or hurdles for industry adoption.
- Scalability and applicability across different types of institutions.
"""

RISK_EXPERT_PROPOSAL_PROMPT = BASE_EXPERT_SYSTEM_PROMPT_TEMPLATE.format(expertise_area="Risk Management in Islamic Finance") + """
Specifically, from a risk management perspective, consider:
- Identification of new risks introduced or existing risks altered by the proposal (Shariah non-compliance, credit, market, operational, legal, reputational).
- Adequacy of proposed or implied risk mitigation techniques.
- Impact on the overall risk profile of Islamic financial institutions.
- Clarity of risk-related definitions and responsibilities.
- Potential for regulatory arbitrage or unintended consequences.
"""

class ExpertAgent(Agent):
    """
    Base class for expert agents analyzing standard enhancement proposals, with tool-calling capabilities.
    """
    DOMAIN_KEYWORDS = DOMAIN_KEYWORDS_FIXED # From components.evaluation.utils

    def __init__(self, system_prompt: str, domain: str):
        self.domain = domain
        # Tools are called programmatically before the main LLM analysis call
        super().__init__(system_prompt=system_prompt, tools=[]) # No tools for LLM to decide on, we call them.

    # --- Tool Methods (from original ExpertEvaluatorAgent) ---
    def _extract_keywords_tool_using_tfidf(self, text_to_analyze: str) -> List[str]:
        logger.info(f"[{self.domain.upper()} TOOL CALL] Extracting keywords with TF-IDF for text ({len(text_to_analyze)} chars)")
        try:
            domain_keywords = self.DOMAIN_KEYWORDS.get(self.domain, [])
            vectorizer, corpus = self._prepare_tfidf_vectorizer_and_corpus(text_to_analyze, domain_keywords)
            doc_scores = self._calculate_keyword_scores(vectorizer, corpus, domain_keywords)
            keywords = self._extract_and_refine_keywords(doc_scores, domain_keywords)
            self._log_extracted_keywords(keywords, text_to_analyze)
            return keywords
        except Exception as e:
            return self._fallback_keyword_extraction(text_to_analyze, e)

    def _prepare_tfidf_vectorizer_and_corpus(self, text: str, domain_keywords: List[str]) -> Tuple[TfidfVectorizer, List[str]]:
        vectorizer = TfidfVectorizer(max_df=0.85, min_df=1, stop_words="english", use_idf=True, ngram_range=(1, 2))
        corpus = [text] + [text[i: i + 200] for i in range(0, len(text), 200) if i + 200 < len(text)] # Shorter snippets
        if not corpus: corpus = [text] # Ensure corpus is not empty

        if domain_keywords:
            domain_doc = " ".join(domain_keywords)
            corpus.append(domain_doc)
            logger.debug(f"[{self.domain.upper()}] Added {len(domain_keywords)} domain keywords for TF-IDF.")
        return vectorizer, corpus

    def _calculate_keyword_scores(self, vectorizer: TfidfVectorizer, corpus: List[str], domain_keywords: List[str]) -> Dict[str, float]:
        if not corpus: return {}
        tfidf_matrix = vectorizer.fit_transform(corpus)
        feature_names = vectorizer.get_feature_names_out()
        doc_scores = dict(zip(feature_names, tfidf_matrix[0].toarray()[0]))
        return self._boost_domain_keywords(doc_scores, domain_keywords, feature_names)

    def _boost_domain_keywords(self, doc_scores: Dict[str, float], domain_keywords: List[str], feature_names: List[str]) -> Dict[str, float]:
        for keyword in domain_keywords:
            if keyword in doc_scores:
                doc_scores[keyword] *= 1.5
            for feature in feature_names:
                if keyword in feature and feature in doc_scores: # For n-grams containing the keyword
                    doc_scores[feature] *= 1.3
        return doc_scores

    def _extract_and_refine_keywords(self, doc_scores: Dict[str, float], domain_keywords: List[str]) -> List[str]:
        if not doc_scores: return domain_keywords[:5] # Fallback if no scores
        sorted_keywords = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        keywords = [keyword for keyword, _ in sorted_keywords[:10]] # Top 10 general keywords

        # Ensure some domain keywords are present if scored
        domain_keywords_to_add = [k for k in domain_keywords if k in doc_scores and k not in keywords and doc_scores[k] > 0.01][:3]
        
        final_keywords = list(dict.fromkeys(keywords + domain_keywords_to_add)) # Combine and keep unique, order matters
        return final_keywords[:12] # Limit total

    def _log_extracted_keywords(self, keywords: List[str], source_text_snippet: str) -> None:
        logger.info(f"[{self.domain.upper()} TOOL RESULT] Extracted keywords: {keywords} from text snippet: '{source_text_snippet[:100]}...'")

    def _fallback_keyword_extraction(self, text: str, error: Exception) -> List[str]:
        logger.error(f"[{self.domain.upper()}] TF-IDF keyword extraction failed: {error}. Using fallback.")
        words = text.lower().split()
        keywords = list(set([w for w in words if len(w) > 3 and w.isalpha()]))[:10]
        domain_fallback = self.DOMAIN_KEYWORDS.get(self.domain, [])[:2]
        return list(set(keywords + domain_fallback))[:12]

    def _search_standards_tool(self, query: str) -> List[Dict[str, Any]]:
        logger.info(f"[{self.domain.upper()} TOOL CALL] Searching standards with query: '{query}'")
        try:
            nodes = retriever.retrieve(query) # Assuming retriever.retrieve returns Node objects
            docs = []
            for node in nodes[:3]:  # Limit to top 3 for conciseness in prompt
                doc_content = {"text": node.text}
                if hasattr(node, 'metadata') and node.metadata:
                    doc_content["metadata"] = node.metadata
                docs.append(doc_content)
            logger.info(f"[{self.domain.upper()} TOOL RESULT] Found {len(docs)} relevant documents for query '{query}'.")
            return docs
        except Exception as e:
            logger.error(f"[{self.domain.upper()}] Error searching standards: {e}")
            return []

    # --- Main Analysis Method ---
    async def analyze_proposal(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a standard enhancement proposal from the expert's domain perspective,
        using tools to gather context.
        """
        proposal_text = context.get("proposal", "")
        previous_discussion_list = context.get("previous_discussion", [])
        
        if not proposal_text:
            logger.warning(f"[{self.domain.upper()}] No proposal text provided for analysis.")
            return {
                "domain": self.domain,
                "analysis": {"text": "Error: No proposal text provided."},
                "concerns": [],
                "recommendations": [],
                "retrieved_documents_count": 0,
                "keywords_used_for_search": []
            }

        # Format previous discussion
        previous_discussion_str = self._format_previous_discussion(previous_discussion_list)

        # 1. Extract Keywords from proposal and discussion
        text_for_keywords = proposal_text + "\n" + previous_discussion_str
        keywords = self._extract_keywords_tool_using_tfidf(text_for_keywords)
        
        # 2. Search Standards using keywords
        retrieved_docs = []
        if keywords:
            search_query = " ".join(keywords)
            retrieved_docs = self._search_standards_tool(search_query)
        
        retrieved_context_str = "No relevant excerpts from existing standards were retrieved for this query."
        if retrieved_docs:
            retrieved_context_str = "Relevant Excerpts from existing AAOIFI standards:\n"
            for i, doc in enumerate(retrieved_docs, 1):
                retrieved_context_str += f"\n--- Document {i} ---\n"
                if doc.get('metadata'):
                    retrieved_context_str += f"Source: {doc['metadata'].get('file_name', 'N/A')}, Section: {doc['metadata'].get('section', 'N/A')}\n"
                retrieved_context_str += f"{doc.get('text', '')}\n"
            retrieved_context_str += "\n--- End of Retrieved Excerpts ---\n"

        # 3. Prepare messages for LLM analysis
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""
Please analyze the following Enhancement Proposal:

ENHANCEMENT PROPOSAL:
{proposal_text}

PREVIOUS DISCUSSIONS:
{previous_discussion_str}

{retrieved_context_str}

Provide your analysis, concerns, and recommendations strictly in the format specified in the system prompt.
            """)
        ]

        # 4. Invoke LLM for analysis
        try:
            # Assuming self.llm.invoke is an async method from the base Agent class
            response =  self.llm.invoke(messages)
            parsed_output = self._parse_structured_response(response.content)
            
            return {
                "domain": self.domain,
                "analysis": {"text": parsed_output.get("ANALYSIS", "Analysis not found in response.")},
                "concerns": [{"type": self.domain, "description": c, "severity": "medium"} for c in parsed_output.get("CONCERNS", [])], # Added default severity
                "recommendations": [{"type": self.domain, "description": r, "priority": "medium"} for r in parsed_output.get("RECOMMENDATIONS", [])], # Added default priority
                "retrieved_documents_count": len(retrieved_docs),
                "keywords_used_for_search": keywords
            }
        except Exception as e:
            logger.error(f"[{self.domain.upper()}] Error during LLM analysis: {e}")
            return {
                "domain": self.domain,
                "analysis": {"text": f"Analysis failed due to an error: {str(e)}"},
                "concerns": [],
                "recommendations": [],
                "retrieved_documents_count": len(retrieved_docs), # Still report what was retrieved
                "keywords_used_for_search": keywords
            }
            
    def _format_previous_discussion(self, discussion_rounds: List[Any]) -> str:
        if not discussion_rounds:
            return "No previous discussion points provided."
        
        formatted_discussion = []
        for i, round_data in enumerate(discussion_rounds):
            # If round_data is a dictionary with 'type' and 'content' fields (from discussion_history)
            if isinstance(round_data, dict) and "type" in round_data:
                round_text = f"--- Discussion Round {round_data.get('round', i+1)} ---\n"
                round_text += f"Expert: {round_data.get('agent', 'Unknown')}\n"
                
                content = round_data.get('content', {})
                # Handle content based on its type
                if isinstance(content, dict):
                    analysis = content.get('analysis', {})
                    # This is where the error likely occurs - ensure we're handling dict properly
                    if isinstance(analysis, dict):
                        analysis_text = analysis.get('text', 'No analysis text.')
                    else:
                        analysis_text = str(analysis)  # Convert non-dict analysis to string
                    round_text += f"Analysis: {analysis_text}\n"
                    
                    concerns = content.get('concerns', [])
                    if concerns:
                        round_text += "Concerns:\n"
                        for concern in concerns:
                            if isinstance(concern, dict):
                                round_text += f"- {concern.get('description', str(concern))}\n"
                            else:
                                round_text += f"- {str(concern)}\n"
                    
                    recommendations = content.get('recommendations', [])
                    if recommendations:
                        round_text += "Recommendations:\n"
                        for rec in recommendations:
                            if isinstance(rec, dict):
                                round_text += f"- {rec.get('description', str(rec))}\n"
                            else:
                                round_text += f"- {str(rec)}\n"
                else:
                    # If content is not a dict, convert it to string safely
                    round_text += f"Content: {str(content)}\n"
                    
            # Legacy format handling with 'opinions' structure
            elif isinstance(round_data, dict) and "opinions" in round_data:
                round_text = f"--- Discussion Round {round_data.get('round', i+1)} ---\n"
                round_text += f"Proposal Discussed: {round_data.get('proposal_discussed', 'N/A')[:200]}...\n"
                opinions = round_data.get('opinions', {})
                
                if opinions:
                    for expert_domain, opinion_data in opinions.items():
                        # Fix potential string concatenation with dict issue here
                        if not isinstance(opinion_data, dict):
                            opinion_data = {"analysis": str(opinion_data), "concerns": [], "recommendations": []}
                        
                        # Safely handle analysis whether it's a dict or not
                        analysis = opinion_data.get('analysis', {})
                        if isinstance(analysis, dict):
                            analysis_text = analysis.get('text', 'No analysis text.')
                        else:
                            analysis_text = str(analysis)
                        
                        concerns_list = opinion_data.get('concerns', [])
                        recommendations_list = opinion_data.get('recommendations', [])
                        
                        round_text += f"  {expert_domain.capitalize()} Expert Opinion:\n"
                        round_text += f"    Analysis Snippet: {analysis_text[:150]}...\n"
                        
                        if concerns_list:
                            round_text += "    Key Concerns: "
                            concern_texts = []
                            for c in concerns_list:
                                if isinstance(c, dict):
                                    concern_texts.append(c.get('description', str(c)))
                                else:
                                    concern_texts.append(str(c))
                            round_text += "; ".join(concern_texts) + "\n"
                        
                        if recommendations_list:
                            round_text += "    Key Recommendations: "
                            rec_texts = []
                            for r in recommendations_list:
                                if isinstance(r, dict):
                                    rec_texts.append(r.get('description', str(r)))
                                else:
                                    rec_texts.append(str(r))
                            round_text += "; ".join(rec_texts) + "\n"
                else:
                    round_text += "No opinions provided.\n"
            
            # Simple string case        
            elif isinstance(round_data, str):
                round_text = f"--- Discussion Round {i+1} ---\n{round_data}\n"
            
            # Fallback for any other format
            else:
                round_text = f"--- Discussion Round {i+1} ---\n{str(round_data)}\n"
                
            formatted_discussion.append(round_text)
        
        return "\n\n".join(formatted_discussion)
        
    def _parse_structured_response(self, text: str) -> Dict[str, Any]:
        """Parse a structured response (ANALYSIS, CONCERNS, RECOMMENDATIONS) into sections."""
        sections: Dict[str, Any] = {"ANALYSIS": "", "CONCERNS": [], "RECOMMENDATIONS": []}
        current_section_key = None
        
        lines = text.split('\n')
        
        for line in lines:
            stripped_line = line.strip()
            
            if stripped_line == "ANALYSIS:":
                current_section_key = "ANALYSIS"
                sections[current_section_key] = "" # Initialize/reset
                continue
            elif stripped_line == "CONCERNS:":
                current_section_key = "CONCERNS"
                sections[current_section_key] = [] # Initialize/reset
                continue
            elif stripped_line == "RECOMMENDATIONS:":
                current_section_key = "RECOMMENDATIONS"
                sections[current_section_key] = [] # Initialize/reset
                continue
            
            if current_section_key:
                if current_section_key == "ANALYSIS":
                    sections[current_section_key] += line + "\n" # Append whole line to keep formatting
                elif current_section_key in ["CONCERNS", "RECOMMENDATIONS"]:
                    # Check if it's a list item (e.g., "1. Concern description")
                    if stripped_line and (stripped_line[0].isdigit() and ". " in stripped_line):
                        item_text = stripped_line.split(". ", 1)[1]
                        sections[current_section_key].append(item_text)
                    elif stripped_line and sections[current_section_key]: # Continuation of previous item
                        sections[current_section_key][-1] += " " + stripped_line
                    elif stripped_line: # First item without numbering or unexpected format
                         sections[current_section_key].append(stripped_line)


        # Clean up analysis text
        if sections["ANALYSIS"]:
            sections["ANALYSIS"] = sections["ANALYSIS"].strip()
        
        # Filter out "None." or similar placeholders if LLM adds them
        for key in ["CONCERNS", "RECOMMENDATIONS"]:
            sections[key] = [item for item in sections[key] if item.lower() not in ["none.", "none", "n/a", "no concerns.", "no recommendations."]]
            
        return sections

# --- Specific Expert Agent Implementations ---

class ShariahExpert(ExpertAgent):
    def __init__(self):
        super().__init__(system_prompt=SHARIAH_EXPERT_PROPOSAL_PROMPT, domain="shariah")

class FinanceExpert(ExpertAgent):
    def __init__(self):
        super().__init__(system_prompt=FINANCE_EXPERT_PROPOSAL_PROMPT, domain="finance")

class StandardsExpert(ExpertAgent):
    def __init__(self):
        super().__init__(system_prompt=STANDARDS_EXPERT_PROPOSAL_PROMPT, domain="standards")

class PracticalExpert(ExpertAgent):
    def __init__(self):
        super().__init__(system_prompt=PRACTICAL_EXPERT_PROPOSAL_PROMPT, domain="practical")

class RiskExpert(ExpertAgent):
    def __init__(self):
        super().__init__(system_prompt=RISK_EXPERT_PROPOSAL_PROMPT, domain="risk")

# Initialize expert agents
shariah_expert = ShariahExpert()
finance_expert = FinanceExpert()
standards_expert = StandardsExpert()
practical_expert = PracticalExpert()
risk_expert = RiskExpert()

# --- Example Usage (Illustrative) ---
# async def main():
#     # Mock retriever and Agent base class if not available for standalone run
#     global retriever
#     class MockNode:
#         def __init__(self, text, metadata=None):
#             self.text = text
#             self.metadata = metadata or {}
#     class MockRetriever:
#         def retrieve(self, query: str) -> List[MockNode]:
#             logger.info(f"MockRetriever called with query: {query}")
#             if "murabaha" in query.lower():
#                 return [
#                     MockNode("Existing Standard FAS 2, Section 3.1: Murabaha requires the seller to possess the asset before selling it to the customer.", {"file_name": "FAS_2.pdf", "section": "3.1"}),
#                     MockNode("Guidance Note on Digital Assets: AAOIFI is currently reviewing the applicability of existing standards to digital assets and tokens.", {"file_name": "Guidance_Digital.pdf", "section": "Intro"})
#                 ]
#             return [MockNode("General AAOIFI Principle: Transactions must be free from excessive uncertainty (Gharar).", {"file_name": "General_Principles.pdf", "section": "2.2"})]
#     retriever = MockRetriever()

#     # Mock Base Agent
#     from langchain_core.outputs import AIMessage as LangchainAIMessage
#     class MockLLM:
#         async def invoke(self, messages):
#             # Simulate LLM response based on messages
#             # For a real test, you'd need an actual LLM (e.g., ChatOpenAI)
#             logger.info("MockLLM invoked.")
#             # Find the HumanMessage content
#             human_content = ""
#             for msg in messages:
#                 if isinstance(msg, HumanMessage):
#                     human_content = msg.content
#                     break
            
#             # Basic response generation
#             response_text = "ANALYSIS:\nThe proposal to use digital tokens in Murabaha transactions without prior physical possession by the fintech company raises significant Shariah concerns, particularly regarding Gharar (uncertainty) and the AAOIFI requirement for possession as noted in retrieved FAS 2, Section 3.1. The previous discussion also highlighted these points. The retrieved guidance note on digital assets suggests this is an evolving area.\n\nCONCERNS:\n1. Potential violation of the Shariah principle of Qabd (possession) before sale in Murabaha, as highlighted by FAS 2.\n2. Increased Gharar due to the intangible nature of tokens and back-to-back transactions without clear ownership transfer.\n\nRECOMMENDATIONS:\n1. The proposal should explicitly detail how constructive possession (Qabd Hukmi) of the underlying commodity represented by the token is achieved by the fintech before offering it to the customer, aligning with AAOIFI interpretations.\n2. Further clarification is needed on the legal nature of the token and its direct, unencumbered claim on the specific commodity batch."
#             if "finance" in messages[0].content.lower(): # System prompt check
#                 response_text = "ANALYSIS:\nFrom a financial accounting perspective, the proposal for digital token Murabaha needs clear guidance on asset recognition. If the fintech doesn't truly control the asset (token/commodity), it cannot be recognized on their books. Revenue recognition timing is also critical.\n\nCONCERNS:\n1. Ambiguity in asset recognition criteria for the digital tokens representing commodities.\n2. Risk of misstating financial position if control is not properly assessed.\n\nRECOMMENDATIONS:\n1. Propose specific accounting entries and criteria for recognizing and derecognizing these digital assets/commodities.\n2. Detail disclosure requirements regarding the nature and risks of such tokenized Murabaha transactions."

#             return LangchainAIMessage(content=response_text)

#     # Replace the actual Agent's LLM with the mock for testing
#     # This requires Agent to have a self.llm attribute
#     # For simplicity, we'll assume ExpertAgent is modified or can take an LLM
#     mock_llm_instance = MockLLM()
#     shariah_expert.llm = mock_llm_instance # Monkey-patching for example
#     finance_expert.llm = mock_llm_instance

#     proposal_context = {
#         "proposal": "We propose a new digital Murabaha platform where a fintech company facilitates the sale of commodity-backed digital tokens. The company enters into a back-to-back transaction, acquiring the token (and underlying commodity interest) only moments before selling it to the end customer. This enhances efficiency.",
#         "previous_discussion": [
#             {"round": 1, "opinions": {"shariah": {"analysis": {"text": "Initial concerns about possession."}, "concerns": [{"description":"Lack of clear possession."}], "recommendations":[]}}, "proposal_discussed": "Initial draft"}
#         ]
#     }

#     print("--- Shariah Expert Analysis ---")
#     shariah_analysis = await shariah_expert.analyze_proposal(proposal_context)
#     print(f"Domain: {shariah_analysis['domain']}")
#     print(f"Keywords: {shariah_analysis['keywords_used_for_search']}")
#     print(f"Retrieved Docs: {shariah_analysis['retrieved_documents_count']}")
#     print(f"Analysis: {shariah_analysis['analysis']['text']}")
#     print(f"Concerns: {shariah_analysis['concerns']}")
#     print(f"Recommendations: {shariah_analysis['recommendations']}")

#     print("\n--- Finance Expert Analysis ---")
#     finance_analysis = await finance_expert.analyze_proposal(proposal_context)
#     print(f"Domain: {finance_analysis['domain']}")
#     print(f"Keywords: {finance_analysis['keywords_used_for_search']}")
#     print(f"Retrieved Docs: {finance_analysis['retrieved_documents_count']}")
#     print(f"Analysis: {finance_analysis['analysis']['text']}")
#     print(f"Concerns: {finance_analysis['concerns']}")
#     print(f"Recommendations: {finance_analysis['recommendations']}")

# if __name__ == "__main__":
#     import asyncio
#     # asyncio.run(main()) # Uncomment to run example