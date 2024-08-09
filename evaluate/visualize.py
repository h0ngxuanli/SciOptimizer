import matplotlib.pyplot as plt
import numpy as np

# Data dictionary containing model names as keys and their performance metrics as values
data = {
    'mistral': {'keywords': 1.0, 'year_range': 0.65, 'authors': 1.0, 'institutions': 0.95, 'conferences': 0.9},
    'gemma': {'keywords': 0.95, 'year_range': 0.4, 'authors': 0.9, 'institutions': 0.9, 'conferences': 0.9},
    'llama3': {'keywords': 1.0, 'year_range': 0.5, 'authors': 0.95, 'institutions': 0.95, 'conferences': 0.9}
}

# Extracting categories
categories = list(data['mistral'].keys())

# Setting up the plot dimensions and labels
fig, ax = plt.subplots(figsize=(10, 6), dpi = 200)
x = np.arange(len(categories))  # Use numpy for better control over tick positions

# Specific colors and markers for each line
styles = {
    'mistral': {'color': 'blue', 'marker': 's', 'linestyle': '-', 'linewidth': 2, 'markersize': 8},
    'gemma': {'color': 'green', 'marker': 'o', 'linestyle': '--', 'linewidth': 2, 'markersize': 8},
    'llama3': {'color': 'red', 'marker': '^', 'linestyle': '-.', 'linewidth': 2, 'markersize': 8},
}

# Plotting each model's performance for each category
for model, performances in data.items():
    ax.plot(x, list(performances.values()), label=model, **styles[model])


# Improving readability of the plot
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=12)
ax.set_ylabel('Accuracy', fontsize=14)
ax.set_title('Evaluation of Keyword Extraction Ability Across Models', fontsize=16)
ax.legend(fontsize = 20)

# Adding a grid for better readability
plt.grid(True, linestyle='--', linewidth=0.5)

plt.show()






import matplotlib.pyplot as plt
import numpy as np

data = {
    'mistral': {
        'summarization': 0.9,
        'experimental findings': 0.85,
        'takeaway message': 0.88,
        'key method': 0.87
    },
    'gemma': {
        'summarization': 0.85,
        'experimental findings': 0.75,
        'takeaway message': 0.8,
        'key method': 0.78
    },
    'llama3': {
        'summarization': 0.95,
        'experimental findings': 0.9,
        'takeaway message': 0.92,
        'key method': 0.9
    }
}

# Extracting categories
categories = list(data['mistral'].keys())

# Setting up the plot dimensions and labels
fig, ax = plt.subplots(figsize=(10, 6), dpi = 200)
x = np.arange(len(categories))  # Use numpy for better control over tick positions

# Specific colors and markers for each line
styles = {
    'mistral': {'color': 'blue', 'marker': 's', 'linestyle': '-', 'linewidth': 2, 'markersize': 8},
    'gemma': {'color': 'green', 'marker': 'o', 'linestyle': '--', 'linewidth': 2, 'markersize': 8},
    'llama3': {'color': 'red', 'marker': '^', 'linestyle': '-.', 'linewidth': 2, 'markersize': 8},
}

# Plotting each model's performance for each category
for model, performances in data.items():
    ax.plot(x, list(performances.values()), label=model, **styles[model])


# Improving readability of the plot
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=12)
ax.set_ylabel('Accuracy', fontsize=14)
ax.set_title('Evaluation of Keyword Extraction Ability Across Models', fontsize=16)
ax.legend(fontsize = 20)

# Adding a grid for better readability
plt.grid(True, linestyle='--', linewidth=0.5)

plt.show()