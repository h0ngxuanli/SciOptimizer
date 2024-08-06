class PromptStore:
    def __init__(self):
        
        keywords_extraction_prompt = """
        Instruction:
        You are assisting a researcher who needs to find academic papers. Extract key search parameters into well-organized categories based on researcher's query. If the query includes abstract date information, calculate time starting from the current year, which is 2024. Please present the findings in a clear, structured list format. 

        Example1:
        User Query: "I need papers from author Michael Smith on machine learning published between 2019 and 2021."
        Keywords: ['machine learning']
        Year Range: [2021, 2020, 2019]
        Authors: ['Michael Smith']
        Institutions: []
        Conferences: []

        Example2:
        User Query: "Find publications related to neural networks in CVPR or ICCV conferences."
        Keywords: ['neural networks']
        Year Range: []
        Authors: []
        Institutions: []
        Conferences: ['CVPR', 'ICCV']

        Example3:
        User Query: "I want studies by Alice Johnson and Bob Lee from Stanford University from the last five years."
        Keywords: []
        Year Range: [2024, 2023, 2022, 2021, 2020]
        Authors: ['Alice Johnson', 'Bob Lee']
        Institutions: ['Stanford University']
        Conferences: []

        Example4:
        User Query: "Search for papers on quantum computing by authors from MIT and Caltech presented at QIP from 2018 to 2020."
        Keywords: ['quantum computing']
        Year Range: [2020, 2019, 2018]
        Authors: []
        Institutions: ['MIT', 'Caltech']
        Conferences: ['QIP']

        New Task:
        User Query: {{$query}}
        """
        self.prompts = {"keywords_extraction_prompt":keywords_extraction_prompt}
        
        
    def get_prompt(self, key):
        return self.prompts[key]
        
    


