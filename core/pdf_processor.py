import pymupdf

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text from PDF bytes in-memory using PyMuPDF.
    
    Args:
        pdf_bytes: Raw bytes of the uploaded PDF file.
    Returns:
        Concatenated text extracted from all pages of the PDF.
    """
    try:
        # Open PDF from stream in-memory
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        text_list = []
        for page in doc:
            # Extract plain text from the page
            page_text = page.get_text()
            if page_text:
                text_list.append(page_text)
        doc.close()
        return "\n".join(text_list)
    except Exception as e:
        print(f"[PDF PROCESSOR ERROR] Failed to extract text from PDF: {e}")
        return ""
