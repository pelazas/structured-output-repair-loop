import os
from typing import Union
from pypdf import PdfReader
from docx import Document

def read_text_file(file_path: str) -> str:
    """Reads content from a .txt file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf(file_path: str) -> str:
    """Extracts text from a .pdf file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

def read_docx(file_path: str) -> str:
    """Extracts text from a .docx file."""
    doc = Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def load_input(input_data: str) -> str:
    """
    Unified loader that handles both raw strings and file paths.
    Automatically detects file type and extracts text.
    """
    # If it's not a path or file doesn't exist, treat as raw text
    if not os.path.isfile(input_data):
        return input_data

    # File type detection based on extension
    _, ext = os.path.splitext(input_data.lower())
    
    if ext == '.txt':
        return read_text_file(input_data)
    elif ext == '.pdf':
        return read_pdf(input_data)
    elif ext in ['.docx', '.doc']:
        return read_docx(input_data)
    else:
        # Fallback to reading as text if extension unknown but it is a file
        try:
            return read_text_file(input_data)
        except Exception:
            raise ValueError(f"Unsupported file format: {ext}")
