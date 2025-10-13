import json
import random
import math
import matplotlib.pyplot as plt
recipe_number = 1
# Load data
with open('recipes_output.json', 'r') as f:
    data = json.load(f)  
recipes = data['recipes']

# Categorize ingredients by function
INGREDIENT_CATEGORIES =  data['categories'][0]
if 'other' not in INGREDIENT_CATEGORIES:
    INGREDIENT_CATEGORIES['other'] = []
def get_category(ingredient_name):
    """Get the category of an ingredient"""
    for category, items in INGREDIENT_CATEGORIES.items():
        if ingredient_name.lower() in items:
            return category
    return 'other'

def validate_recipe(recipe):
    """Check if recipe has minimum required ingredients"""
    categories = set()
    for ing in recipe['ingredients']:
        categories.add(get_category(ing['ingredient']))
    
    required = {'flour', 'fat', 'sugar', 'eggs', 'leavening'}
    return required.issubset(categories)

def calculate_balance_score(recipe):
    """Score recipe based on ingredient proportions"""
    # Group by category
    category_amounts = {}
    for ing in recipe['ingredients']:
        cat = get_category(ing['ingredient'])
        category_amounts[cat] = category_amounts.get(cat, 0) + ing['amount']
    
    # Ideal ratios (approximate)
    ideal_ratios = {
        'flour': 2.5, # tsp
        'fat': 1.0, # tsp
        'sugar': 1.0, # tsp
        'eggs': 2.0,  # count
        'leavening': 1.0,  # tsp
    }
    
    # Calculate deviation from ideal ratios
    score = 1.0
    for cat, ideal in ideal_ratios.items():
        if cat in category_amounts:
            actual = category_amounts[cat]
            # Penalize deviation from ideal
            ratio = min(actual, ideal) / max(actual, ideal)
            score *= (0.5 + 0.5 * ratio)
        else:
            score *= 0.5  # Missing category penalty
    
    return score

def calculate_fitness(recipe):
    """Custom fitness function"""
    if not validate_recipe(recipe):
        return 0.0
    
    # Base rating
    avg_rating = sum(i['rating'] for i in recipe['ingredients']) / len(recipe['ingredients'])
    
    # Balance score
    balance = calculate_balance_score(recipe)
    
    # Diversity bonus (but not too many ingredients)
    num_ingredients = len(recipe['ingredients'])
    diversity = 1.0 # [5, 8] ingredient counts
    if 8 <= num_ingredients <= 12:
        diversity = 1.2
    elif num_ingredients < 5:
        diversity = 0.7
    elif num_ingredients > 15:
        diversity = 0.8
    
    # Complexity penalty for too many duplicate categories
    categories = [get_category(i['ingredient']) for i in recipe['ingredients']]
    unique_cats = len(set(categories))
    complexity = unique_cats / len(categories)
    
    return avg_rating * balance * diversity * complexity * 10

def crossover(r1, r2):
    """Crossover that preserves recipe structure"""
    global recipe_number
    
    # Group ingredients by category
    def group_by_category(recipe):
        groups = {}
        for ing in recipe['ingredients']:
            cat = get_category(ing['ingredient'])
            if cat not in groups:
                groups[cat] = []
            groups[cat].append(ing)
        return groups
    
    g1 = group_by_category(r1)
    g2 = group_by_category(r2)
    
    # Combine categories, randomly choosing from parent 1 or 2
    new_ingredients = []
    all_cats = set(list(g1.keys()) + list(g2.keys()))
    
    for cat in all_cats:
        if cat in g1 and cat in g2:
            # Choose from either parent
            source = g1 if random.random() < 0.5 else g2
            new_ingredients.extend([ing.copy() for ing in source[cat]])
        elif cat in g1:
            new_ingredients.extend([ing.copy() for ing in g1[cat]])
        else:
            new_ingredients.extend([ing.copy() for ing in g2[cat]])
    
    # Ensure we have at least some ingredients
    if len(new_ingredients) == 0:
        new_ingredients = [random.choice(r1['ingredients']).copy()]
    
    r = {
        'name': f"recipe {recipe_number}",
        'ingredients': new_ingredients
    }
    recipe_number += 1
    
    return r

def mutation(recipe):
    """Mutation that maintains recipe validity"""
    mutation_type = random.randint(0, 4)
    
    # Adjust amount
    if mutation_type == 0 and len(recipe['ingredients']) > 0:
        i = random.randint(0, len(recipe['ingredients'])-1)
        recipe['ingredients'][i] = recipe['ingredients'][i].copy()
        change = random.uniform(0.8, 1.2)
        recipe['ingredients'][i]['amount'] = max(0.1, recipe['ingredients'][i]['amount'] * change)
    
    # Swap ingredient within same category
    elif mutation_type == 1 and len(recipe['ingredients']) > 0:
        i = random.randint(0, len(recipe['ingredients'])-1)
        old_ing = recipe['ingredients'][i]
        cat = get_category(old_ing['ingredient'])
        
        if cat in INGREDIENT_CATEGORIES:
            same_category = INGREDIENT_CATEGORIES[cat]
            # Find an ingredient from recipes in same category
            candidates = [ing for r in recipes for ing in r['ingredients'] 
                         if ing['ingredient'] in same_category]
            if candidates:
                new_ing = random.choice(candidates).copy()
                new_ing['amount'] = old_ing['amount']
                recipe['ingredients'][i] = new_ing
    
    # Add ingredient from a missing category
    elif mutation_type == 2:
        current_cats = {get_category(i['ingredient']) for i in recipe['ingredients']}
        missing_cats = set(INGREDIENT_CATEGORIES.keys()) - current_cats
        
        if missing_cats:
            cat = random.choice(list(missing_cats))
            candidates = [ing for r in recipes for ing in r['ingredients'] 
                         if get_category(ing['ingredient']) == cat]
            if candidates:
                recipe['ingredients'].append(random.choice(candidates).copy())
    
    # Remove non-essential ingredient
    elif mutation_type == 3 and len(recipe['ingredients']) > 5:
        # Don't remove essential categories
        non_essential_idx = [
            i for i, ing in enumerate(recipe['ingredients'])
            if get_category(ing['ingredient']) in ['addins', 'flavoring', 'liquid', 'other']
        ]
        if non_essential_idx:
            recipe['ingredients'].pop(random.choice(non_essential_idx))
    
    # Duplicate a good ingredient (for add-ins)
    elif mutation_type == 4:
        addins = [ing for ing in recipe['ingredients'] 
                 if get_category(ing['ingredient']) == 'addins']
        if addins:
            recipe['ingredients'].append(random.choice(addins).copy())

def normalise_recipe(r):
    """Normalize recipe amounts"""
    # First, combine duplicate ingredients
    unique_ingredients = {}
    for i in r['ingredients']:
        if i['ingredient'] in unique_ingredients:
            n = unique_ingredients[i['ingredient']]
            n['amount'] += i['amount']
        else:
            unique_ingredients[i['ingredient']] = i.copy()
    r['ingredients'] = list(unique_ingredients.values())
    
    # Convert to common unit (teaspoons) for scaling calculation
    def to_teaspoons(amount, unit):
        conversions = {
            'cup': 48,
            'tablespoon': 3,
            'teaspoon': 1,
            'ounce': 6,  # approximate for dry ingredients
            'egg': 12    # approximate volume of an egg
        }
        return amount * conversions.get(unit, 1)
    
    # Calculate total in teaspoons
    total_tsp = sum(to_teaspoons(i['amount'], i['unit']) for i in r['ingredients'])
    
    # Target: reasonable cookie batch (about 240 tsp total = 5 cups flour equivalent)
    target_tsp = 240
    scale = target_tsp / total_tsp if total_tsp > 0 else 1
    
    # Scale each ingredient
    for i in r['ingredients']:
        i['amount'] = round(i['amount'] * scale, 2)
        
        # Ensure minimum amounts make sense
        if i['unit'] == 'cup':
            i['amount'] = max(0.25, i['amount'])
        elif i['unit'] == 'teaspoon':
            i['amount'] = max(0.25, i['amount'])
        elif i['unit'] == 'tablespoon':
            i['amount'] = max(0.5, i['amount'])
        elif i['unit'] == 'egg':
            i['amount'] = max(1.0, round(i['amount']))  # Round eggs to whole numbers




#   "categories":
#   [
#     {
#       "flour": [
#         "all purpose flour",
#         "bread flour",
#         "cake flour",
#         "wheat flour",
#         "brown rice flour"
#       ],
#       "fat": [
#         "butter",
#         "shortening",
#         "margarine",
#         "vegetable oil"
#       ],
#       "sugar": [
#         "sugar",
#         "brown sugar"
#       ],
#       "eggs": [
#         "egg"
#       ],
#       "leavening": [
#         "baking soda",
#         "baking powder"
#       ],
#       "liquid": [
#         "milk",
#         "water",
#         "sour cream"
#       ],
#       "flavoring": [
#         "vanilla",
#         "almond extract",
#         "coconut extract"
#       ],
#       "addins": [
#         "chocolate chip",
#         "walnut",
#         "pecan",
#         "oat",
#         "raisins",
#         "nuts"
#       ]
#     }
#   ]