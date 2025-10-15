import csv
import json
from collections import defaultdict

def transform_csv_to_json(csv_file_path, output_json_path):
    recipes_dict = defaultdict(lambda: {
        'name': '',
        'ingredients': []
    })
    
    with open(csv_file_path, 'r', encoding='iso-8859-1') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            recipe_name = row['Recipe_Index'].strip()

            if not recipes_dict[recipe_name]['name']:
                recipes_dict[recipe_name]['name'] = recipe_name
            
            # Convert amount to float
            try:
                amount = float(row['Quantity']) if row['Quantity'] else 0.0
            except ValueError:
                amount = 0.0
            
            # Convert rating to float
            try:
                rating = 0.5 if (row['Rating'] == "NA" or not row['Rating']) else float(row['Rating'].strip())
            except ValueError:
                rating = 0.5

            ingredient_data = {
                'ingredient': row['Ingredient'].strip().lower() if row['Ingredient'] else "",
                'amount': amount,
                'unit': row['Unit'].strip() if row['Unit'] else "",
                'rating': rating
            }
            
            recipes_dict[recipe_name]['ingredients'].append(ingredient_data)

    recipes_list = [recipe_data for recipe_data in recipes_dict.values()]
    
    output_data = {
        'recipes': recipes_list
    }
    
    with open(output_json_path, 'w', encoding='utf-8') as jsonfile:
        jsonfile.write('{\n  "recipes": [\n')
        
        for i, recipe in enumerate(recipes_list):
            jsonfile.write('    {\n')
            jsonfile.write(f'      "name": "{recipe["name"]}",\n')
            jsonfile.write('      "ingredients": [\n')
            
            for j, ing in enumerate(recipe['ingredients']):
                comma = ',' if j < len(recipe['ingredients']) - 1 else ''
                jsonfile.write(f'        {{ "ingredient": "{ing["ingredient"]}",  "amount": {ing["amount"]},  "unit": "{ing["unit"]}",  "rating": {ing["rating"]} }}{comma}\n')
            
            recipe_comma = ',' if i < len(recipes_list) - 1 else ''
            jsonfile.write(f'      ]\n')
            jsonfile.write(f'    }}{recipe_comma}\n')
        
        jsonfile.write('  ]\n')
        jsonfile.write('}\n')
    
    print(f"Successfully transformed {len(recipes_list)} recipes")
    print(f"Output saved to: {output_json_path}")
    
    return output_data


if __name__ == "__main__":

    csv_file = "2_Scaled_Units_Cleaned.csv"
    output_file = "recipes_output.json"
    
    result = transform_csv_to_json(csv_file, output_file)
    
    if result['recipes']:
        print("\nSample - First recipe:")
        print(json.dumps(result['recipes'][0], indent=2))