import os
import json
import pandas as pd

json_path = os.path.join(os.path.dirname(__file__), '../../timsconvert/parameter_descriptions.json')

with open(json_path, 'r') as json_file:
    descriptions = json.load(json_file)

csv_path = os.path.join('source', 'parameter_descriptions.csv')

pd.DataFrame({'Parameter': list(descriptions.keys()),
              'Description': list(descriptions.values())}).to_csv(csv_path, index=False)
