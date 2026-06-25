import json

# Load the original file
with open('food-enforcement-0001-of-0001.json', 'r') as f:
    data = json.load(f)

# Extract just the results array
results = data['results']

# Save as a new file
with open('recalls.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"Extracted {len(results)} records to recalls.json")