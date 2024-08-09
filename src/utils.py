import fitz  # PyMuPDF for handling PDF files
import re  # Regular expression library

def extract_parameters(output):
    """Extract search parameters from text based on predefined keys."""
    
    # example output = """
    # * *keywords ['graph neural networks']
    # * **Year Range:** [2022]
    # * **Authors []
    # * **Institutions:** []
    # * **Conferences:** []
    # """
    
    # Define a dictionary to store the extracted parameters
    params = {
        'keywords': [],
        'year_range': [],
        'authors': [],
        'institutions': [],
        'conferences': []
    }

    # List of keys we're interested in extracting, aligned with params keys
    possible_keys = ['keywords', 'year range', 'authors', 'institutions', 'conferences']
    lines = output.split('\n')  # Split the output text into lines
    
    for line in lines:
        line = line.lower()  # Normalize the line for case insensitivity
        key_found = None
        # Determine if the line contains any of the possible keys
        for key in possible_keys:
            if key in line:
                key_found = key
                break
        if key_found:
            normalized_key = key_found.replace(' ', '_')  # Normalize the key to match params dictionary keys
            # Extract values enclosed in brackets
            start_index, end_index = line.find('['), line.rfind(']') + 1
            if start_index != -1 and end_index != -1:
                value_str = line[start_index:end_index].strip()
                # Safely parse and clean the list items
                cleaned_values = [item.strip().strip("'\"") for item in value_str.strip('[]').split(',')]
                params[normalized_key] = cleaned_values if cleaned_values != [''] else []

    return params

def extract_text_from_pdf(pdf_path):
    
    """Extract text from a PDF file up to a section labeled 'References'."""
    
    doc = fitz.open(pdf_path)  # Open the PDF file
    text = ""
    # Regex to identify the 'References' header, ignoring leading/trailing whitespace
    references_pattern = re.compile(r'^\s*references\s*$', re.IGNORECASE)

    # Process each page in the PDF
    for page in doc:
        page_text = page.get_text("text")  # Get text from the page
        page_lines = page_text.splitlines()  # Split text into lines
        
        for line in page_lines:
            if references_pattern.search(line.strip()):
                break  # Stop reading if 'References' is found
            text += line + "\n"
        else:
            # Continue to the next page if 'References' not found in current page
            continue
        # Exit loop if 'References' found
        break

    return text