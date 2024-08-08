
import fitz  # Import PyMuPDF
import re  # Import the regular expression library


def extract_parameters(output):
    # Initialize the dictionary to hold extracted parameters
    params = {
        'keywords': [],
        'year_range': [],
        'authors': [],
        'institutions': [],
        'conferences': []
    }

    # Define possible keys for recognition
    possible_keys = ['keywords', 'year range', 'authors', 'institutions', 'conferences']

    # Split the output into lines
    lines = output.split('\n')
    
    # Process each line to extract parameters
    for line in lines:
        # Normalize the line for case insensitivity
        line = line.lower()
        # Extract the key by finding the first keyword that appears in the line
        key_found = None
        for key in possible_keys:
            if key in line:
                key_found = key
                break
        
        if key_found:
            # Normalize the key to match dictionary keys
            normalized_key = key_found.replace(' ', '_')
            # Look for the list enclosed in brackets
            start_index = line.find('[')
            end_index = line.rfind(']') + 1
            if start_index != -1 and end_index != -1:
                # Extract the substring for the list and safely parse it
                value_str = line[start_index:end_index].strip()
                cleaned_values = [item.strip().strip("'\"") for item in value_str.strip('[]').split(',')]
                
                params[normalized_key] = cleaned_values if cleaned_values != [''] else []

    return params






def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    text = ""
    references_pattern = re.compile(r'^[^\S\r\n]*references[^\S\r\n]*$', re.IGNORECASE)  # Regex for 'References' on a single line, case-insensitive

    # Iterate through each page
    for page in doc:
        # Extract text from the page
        page_text = page.get_text("text")
        page_lines = page_text.splitlines()  # Split text into lines
        
        # Iterate through each line
        for line in page_lines:
            # Check if the line matches 'References', case-insensitive
            if references_pattern.search(line.strip()):
                break  # Break if 'References' is found
            else:
                # Continue appending text if not found
                text += line + "\n"
        else:
            # Continue to next page if 'References' not found in current page
            continue
        # Break outer loop if 'References' found
        break

    return text

# def extract_text_from_pdf(pdf_path):
#     # Open the PDF file
#     doc = fitz.open(pdf_path)
#     text = ""
#     # Iterate through each page
#     for page in doc:
#         # Extract text from the page
#         text += page.get_text()
#     return text

