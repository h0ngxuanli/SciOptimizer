"""
Get Evaluations 
"""
import re
import json

root_dir = "./evaluate"
def load_json(root_dir, model):
    with open(root_dir + "/" + f"outputs_{model}.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data[model]

def evaluate_accuracy(actual_list, predicted_list):
    results = {
        'keywords': 0,
        'year_range': 0,
        'authors': 0,
        'institutions': 0,
        'conferences': 0
    }
    
    total_cases = len(actual_list)

    for actual, predicted in zip(actual_list, predicted_list):
        # Evaluate Keywords
        actual_keywords = set(re.findall(r'\w+', ' '.join(actual['keywords']).lower()))
        predicted_keywords = set(re.findall(r'\w+', ' '.join(predicted['keywords']).lower()))
        if actual_keywords & predicted_keywords:
            results['keywords'] += 1
        
        # Evaluate Year Range
        if set(actual['year_range']) == set(predicted['year_range']):
            results['year_range'] += 1
        
        # Evaluate Authors
        actual_authors = set([author.lower() for author in actual['authors']])
        predicted_authors = set([author.lower() for author in predicted['authors']])
        if actual_authors == predicted_authors:
            results['authors'] += 1
        
        # Evaluate Institutions
        if set([inst.lower() for inst in actual['institutions']]) == set([inst.lower() for inst in predicted['institutions']]):
            results['institutions'] += 1
        
        # Evaluate Conferences
        if set([conf.lower() for conf in actual['conferences']]) == set([conf.lower() for conf in predicted['conferences']]):
            results['conferences'] += 1

    # Calculate accuracy for each key
    for key in results:
        results[key] = results[key] / total_cases

    return results


baseline = load_json(root_dir, "baseline")


evaluation_results = {}
for model in [ "mistral", "gemma", "llama3"]:
    prediction = load_json(root_dir, model)
    
    evaluation_results[model] = evaluate_accuracy(baseline, prediction)
    
print(evaluation_results)