import re
import fitz  # PyMuPDF
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import NoEscape
from typing import List, Dict

# STEP 1: Parse clause numbers using regex
def parse_clauses_by_number(text: str) -> Dict[str, str]:
    # Matches things like 2/3/1 or 1.1.1 or 2.4/3 etc.
    pattern = re.compile(r"(?<=\n)(\d+(?:[/\.]\d+)+)\s+(.*?)(?=\n\d|$)", re.DOTALL)
    clauses = {}
    for match in pattern.finditer(text):
        clause_id = match.group(1).strip()
        clause_text = match.group(2).strip().replace('\n', ' ')
        clauses[clause_id] = clause_text
    return clauses
import os

def generate_updated_standard_pdf(original_pdf_path: str, enhancements: List[Dict], output_path: str):
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Start LaTeX document
    doc = Document("AAOIFI_Enhanced_Standard")

    # Step 1: Extract text from PDF
    with fitz.open(original_pdf_path) as pdf:
        full_text = ""
        for page in pdf:
            full_text += page.get_text()

    # Step 2: Parse by clauses
    clauses = parse_clauses_by_number(full_text)

    # Step 3: Apply enhancements
    for enhancement in enhancements:
        clause_id = enhancement['clause_id']
        if clause_id in clauses:
            print(f"Enhancing clause: {clause_id}")
            clauses[clause_id] = enhancement['proposed_text']

    # Step 4: Write structured content
    with doc.create(Section("AAOIFI Standard (Enhanced)")):
        for clause_id in sorted(clauses):
            with doc.create(Subsection(f"Clause {clause_id}")):
                doc.append(NoEscape(clauses[clause_id]))

    # Step 5: Generate PDF
    doc.generate_pdf(output_path, clean_tex=False)
    print(f"\n✅ Enhanced standard PDF saved to: {output_path}.pdf")
