import PyPDF2
from docx import Document
import io

SUPPORTED_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']

def process_files(files):
    proposals = []
    
    for file in files:
        if file.content_type not in SUPPORTED_TYPES:
            raise ValueError(f"Unsupported file type: {file.content_type}")
            
        content = ""
        file.stream.seek(0)
        
        if file.content_type == 'application/pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            content = " ".join([page.extract_text() for page in pdf_reader.pages])
        else:
            doc = Document(io.BytesIO(file.read()))
            content = "\n".join([para.text for para in doc.paragraphs])
        
        proposals.append({
            "filename": file.filename,
            "content": content[:15000]  # Limit to first 15k characters
        })
    
    return proposals