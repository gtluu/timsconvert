import json
import pandas as pd

with open('../../timsconvert/parameter_descriptions.json', 'r') as json_file:
    descriptions = json.load(json_file)


pd.DataFrame({'Parameter': list(descriptions.keys()),
              'Description': list(descriptions.values())}).to_csv('parameter_descriptions.csv', index=False)
