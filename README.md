# Research Optimizer


# Demo Video


<iframe width="560" height="315" src="https://www.youtube.com/watch?v=xTO6nFuMaSM" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


# Motivation

- Given the rapid evolution of transformer models, it is crucial to have timely access to the latest findings.

- A highly flexible and efficient paper management system is necessary for researchers to capture the newest trends.

# Key Features

### 1. Retrieve relevant papers
- Functionality: 
    - retrieve relevant papers based on user query
- API Supported: 
    - arXiv 
    - google scholar
    - semantic scholar
- Results Storage:
    - Save metadata to CSV file
    - Save metadata to Zotero

### 2. Fine-grained retrieval
- Functionality: 
    - further narrow down search results based on specific criteria
- Fine-grained filters:
    - Authors: Filter results by specifying one or more authors.
    - Publication Year: Limit search results to a specific year or range of years.
    - Publisher: Filter papers by the conference or journal.
    - Affiliation: Search for papers based on the affiliations of the authors.
    - Custom Keywords: defined by user


### 3. Generate Reference
- Functionality: 
    - Automatically generate references in any desired format.


### 4. Get Information of Paper that cites the paper
- Functionality: 
    - Retrieve metadata of papers that cite a specific paper

### 5. Generate survey table
- Functionality:
    - Build a customized survey table to summarize papers
- Customization:
    - Allow users to define specific columns in the survey table, tailored to their research needs
    - Each column will contain specific information extracted from the papers
- Example:
    - Takeaway: Key takeaway messages or conclusions from the paper
    - Methodology: Brief description of the methodologies used in the research

### 6. Automatic Updates

- Functionality:
    - The agent will periodically (daily, weekly, or as specified) run these preset searches and save the results
    - Users will be notified of newly retrieved papers via email

# Time Line (Weeks)

- (5) Implement the basic function: retrive papers based on user query
- (6) Implement fine-grained filters
- (7) Implement reference generation & citing paper retrival 
- (8) Implement survey table generation
- (9) Implement automatic updates 
- (10) Ensure CI/CD is robust and dockerizes & Documentation and Clean up