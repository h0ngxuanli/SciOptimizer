def extract_parameters(output):
    # Initialize the dictionary to hold extracted parameters
    params = {
        'keywords': [],
        'year_range': [],
        'authors': [],
        'institutions': [],
        'conferences': []
    }

    # Split the output into lines
    lines = output.split('\n')
    
    # Process each line to extract parameters
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')  # Normalize the key to match parameter names
            if key in params:
                # Remove spaces, strip the line, evaluate the list
                params[key] = eval(value.strip())

    return params