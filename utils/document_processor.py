import magic
from typing import Dict, Any
from unstructured.partition.pdf import partition_pdf

class DocumentProcessor:
    """Handles document processing for compliance verification"""
    
    @staticmethod
    def read_pdf(file_path: str) -> str:
        """Extract text content from PDF file using unstructured library"""
        elements = partition_pdf(filename=file_path)
        text_content = "\n".join([element.text for element in elements if element.text])
        return text_content
    
    @staticmethod
    def get_file_type(file_path: str) -> str:
        """Detect file type using python-magic"""
        return magic.from_file(file_path, mime=True)
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process document and return structured content"""
        file_type = self.get_file_type(file_path)
        
        if file_type == 'application/pdf':
            content = self.read_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        print("File Content:")
        print(content)
        print()
            
        return {
            "content": content,
            "metadata": {
                "file_type": file_type,
                "file_path": file_path
            }
        }
