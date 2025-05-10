from utils.document_processor import DocumentProcessor
from components.agents.compliance_verfiier import ComplianceVerifierAgent

def verify_document_compliance(file_path: str, verbose: bool = False):
    """Run compliance verification on a document"""
    try:
        # Initialize processors
        doc_processor = DocumentProcessor()
        compliance_verifier = ComplianceVerifierAgent()
        
        # Process document
        if verbose:
            logging.info(f"Processing document: {file_path}")
        
        doc_content = doc_processor.process_document(file_path)
        
        # # Verify compliance
        # if verbose:
        #     logging.info("Verifying compliance...")
            
        result = compliance_verifier.verify_compliance(doc_content["content"])
        
        # Print results
        print("\nCompliance Verification Results:")
        print("=" * 50)
        print(result["compliance_report"])
        
    except Exception as e:
        logging.error(f"Error during compliance verification: {str(e)}")
        sys.exit(1)