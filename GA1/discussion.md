# Gather an Inspiring Set for Cookie/Cake Recipes

- [Choco cookie](https://github.com/elleobrien/Average_Cookie)

# Create a Knowledgebase for the Inspiring Set

- Cleaned data in form of json
  - The rating for each ingredient across one recipe is identical

```json
  "recipes": [
    {
      "name": "[recipe_name]",
      "ingredients": [
        {
          "ingredient": "ingredient_name",
          "amount": "numerical_amount",
          "unit": "unit_type",
          "rating": "numerical_rating_from_source"
        }
      ]
    }
  ]
```

- Extra category information for fitness calculation, necessary ingredient guarantee and structure preservation

```json
  "categories": [
    {
      "[category_name]": [
          "[ingredient1_name]",
          "[ingredient2_name]"
      ]
    }
  ]
```

# Implement a Recipe Generator using a Genetic Algorithm

- Fitness Calculation
  - $\text{base rating}\times\text{balance score}\times\text{diversity score}\times 10$
  - _base rating_: the initial rating for the ingredient
  - _balance score_: how ingredients are distributed compared with an ideal ratio
  - _diversity score_:
    - $0.7$ if num_ingredients $\in [0,5)$
    - $1$ if num_ingredients $\in [5,8]$
    - $1.2$ if num_ingredients $\in (8,12]$
    - $0.8$ if num_ingredients $\in (12,\infty)$
  - _$10$_: scale up for demostration
- The 1st generation
  - Tournament Selection
    - Randomly pick $k$ individuals
    - Select the best among them
    - Repeat to get all parents
      - In our case $k=10$
- How to crossover
  - Preserve parent recipes' category structure using category information
  - Combine categories, randomly choosing from parent 1 or 2
  - Ensure there are at least some new ingredients
- How to mutate
  - Maintain recipe validity
  - Regular mutation
    - Adjust amount
    - Swap ingredient within same category
    - Add ingredient from a missing category
    - Remove non-essential ingredient
    - Duplicate a good ingredient (for add-ins)
  - Probability set as 0.5 after several trials
    - Higher would be unstable
    - Lower would lead to low diversity
- How to form a new generation
  - Normalize recipe amounts so that the new recipe avoids having something like 1000 cups of milk
- Stopping criteria
  - After 200 rounds of generation return the best recipe found by that far
  - Non-interactive since we consider user control as not helpful
    - Humans cannot either generate a vague image of the cookie based on textual recipe nor evaluate the recipe

# Creativity Evaluation

# Present Generated Recipes in a Small Cookbook

- GenAI API calling for prompt generation
- Use the prompt to generate images
- Output a PDF as required

# Report

- [ICCC Template](https://www.overleaf.com/2899441438jrkzbbqrnmxp#b43bf2)
