import ga
def evaluate_novelty(generated_recipe, original_recipes):
    """Measure how different the recipe is from the training set"""
    
    # Ingredient novelty
    gen_ingredients = set(i['ingredient'] for i in generated_recipe['ingredients'])
    
    # Find most similar recipe in original set
    max_similarity = 0
    for orig in original_recipes:
        orig_ingredients = set(i['ingredient'] for i in orig['ingredients'])
        
        # Jaccard similarity
        intersection = len(gen_ingredients & orig_ingredients)
        union = len(gen_ingredients | orig_ingredients)
        similarity = intersection / union if union > 0 else 0
        max_similarity = max(max_similarity, similarity)
    
    novelty_score = 1 - max_similarity
    return novelty_score

def evaluate_combination_novelty(generated_recipe, original_recipes):
    """Check if ingredient combinations are novel"""
    
    # Extract all ingredient pairs from generated recipe
    gen_ingredients = [i['ingredient'] for i in generated_recipe['ingredients']]
    gen_pairs = set()
    for i in range(len(gen_ingredients)):
        for j in range(i+1, len(gen_ingredients)):
            gen_pairs.add(tuple(sorted([gen_ingredients[i], gen_ingredients[j]])))
    
    # Check how many pairs appear in original recipes
    original_pairs = set()
    for recipe in original_recipes:
        orig_ingredients = [i['ingredient'] for i in recipe['ingredients']]
        for i in range(len(orig_ingredients)):
            for j in range(i+1, len(orig_ingredients)):
                original_pairs.add(tuple(sorted([orig_ingredients[i], orig_ingredients[j]])))
    
    novel_pairs = gen_pairs - original_pairs
    combination_novelty = len(novel_pairs) / len(gen_pairs) if gen_pairs else 0
    
    return combination_novelty

def evaluate_value(recipe):
    """Assess the quality/usefulness of the recipe"""
    # Extract components from fitness function
    scores = {
        'rating': sum(i['rating'] for i in recipe['ingredients']) / len(recipe['ingredients']),
        'balance': ga.calculate_balance_score(recipe),
        'diversity': calculate_diversity_score(recipe),
        'validity': 1.0 if ga.validate_recipe(recipe) else 0.0
    }
    
    return scores

def calculate_diversity_score(recipe):
    """Extract diversity score from your fitness function"""
    num_ingredients = len(recipe['ingredients'])
    if 8 <= num_ingredients <= 12:
        return 1.2
    elif num_ingredients < 5:
        return 0.7
    elif num_ingredients > 15:
        return 0.8
    return 1.0

def evaluate_typicality(generated_recipe, original_recipes):
    """How 'cookie-like' is the recipe?"""
    
    # Check if it has typical cookie proportions
    category_amounts = {}
    for ing in generated_recipe['ingredients']:
        cat = ga.get_category(ing['ingredient'])
        category_amounts[cat] = category_amounts.get(cat, 0) + ing['amount']
    
    # Compare to average proportions in original recipes
    avg_proportions = calculate_average_proportions(original_recipes)
    
    typicality = 0
    for cat, amount in category_amounts.items():
        if cat in avg_proportions:
            expected = avg_proportions[cat]
            ratio = min(amount, expected) / max(amount, expected)
            typicality += ratio
    
    return typicality / len(category_amounts)

def calculate_average_proportions(recipes):
    """Calculate average ingredient proportions across all recipes"""
    all_proportions = {cat: [] for cat in ga.INGREDIENT_CATEGORIES.keys()}
    
    for recipe in recipes:
        category_amounts = {}
        for ing in recipe['ingredients']:
            cat = ga.get_category(ing['ingredient'])
            category_amounts[cat] = category_amounts.get(cat, 0) + ing['amount']
        
        for cat, amount in category_amounts.items():
            all_proportions[cat].append(amount)
    
    return {cat: sum(amounts)/len(amounts) for cat, amounts in all_proportions.items() if amounts}

def evaluate_creativity(recipe, original_recipes):
    """
    Combine novelty and value for overall creativity assessment
    Based on Boden's framework: Creative = Novel + Valuable
    """
    
    # Novelty components (how different/surprising)
    ingredient_novelty = evaluate_novelty(recipe, original_recipes)
    combination_novelty = evaluate_combination_novelty(recipe, original_recipes)
    novelty = (ingredient_novelty + combination_novelty) / 2
    
    # Value components (how good/useful)
    value_scores = evaluate_value(recipe)
    value = (value_scores['rating'] + value_scores['balance'] + 
             value_scores['diversity']) / 3
    
    # Typicality (should still be recognizable as a cookie)
    typicality = evaluate_typicality(recipe, original_recipes)
    
    # Creativity = high novelty + high value + reasonable typicality
    # We want novel but not too weird (typicality penalty if too low)
    typicality_penalty = 1.0 if typicality > 0.3 else 0.5
    
    creativity_score = (novelty + value) * typicality_penalty /2
    
    return {
        'creativity': creativity_score,
        'novelty': novelty,
        'value': value,
        'typicality': typicality,
        'components': {
            'ingredient_novelty': ingredient_novelty,
            'combination_novelty': combination_novelty,
            **value_scores
        }
    }

