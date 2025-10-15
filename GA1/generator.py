import json
import random
import math
import matplotlib.pyplot as plt
import creativity_evaluation
import ga
# Initialize population
population_size = 100
recipe_number = 1

population = random.choices(ga.recipes, k=population_size)
for r in population:
    r['fitness'] = ga.calculate_fitness(r)
population = sorted(population, reverse=True, key=lambda r: r['fitness'])

# Evolution
max_fitnesses = []
avg_fitnesses = []
generations = 200

for gen in range(generations):
    # Generate offspring
    offspring = []
    while len(offspring) < population_size:
        # Tournament selection
        tournament_size = 10
        tournament = random.sample(population, tournament_size)
        p1 = max(tournament, key=lambda r: r['fitness'])
        tournament = random.sample(population, tournament_size)
        p2 = max(tournament, key=lambda r: r['fitness'])
        
        # Crossover
        child = ga.crossover(p1, p2)
        
        # Mutation with probability
        if random.random() < 0.5:
            ga.mutation(child)
        
        ga.normalise_recipe(child)
        child['fitness'] = ga.calculate_fitness(child)
        offspring.append(child)
    
    # Elitism: keep top 10%
    elite_size = population_size // 10
    population = sorted(population, reverse=True, key=lambda r: r['fitness'])
    population = population[:elite_size] + offspring[:(population_size - elite_size)]
    population = sorted(population, reverse=True, key=lambda r: r['fitness'])
    
    max_fitnesses.append(population[0]['fitness'])
    avg_fitnesses.append(sum(r['fitness'] for r in population) / len(population))
    
    if gen % 20 == 0:
        print(f"Generation {gen}: Best fitness = {population[0]['fitness']:.3f}, Avg = {avg_fitnesses[-1]:.3f}")

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(max_fitnesses, label="Best Fitness", linewidth=2)
plt.plot(avg_fitnesses, label="Average Fitness", linewidth=2)
plt.xlabel("Generation")
plt.ylabel("Fitness")
plt.title("Cookie Recipe Evolution")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

print("\n" + "="*40)
print("CREATIVITY EVALUATION")
print("="*40)

# Evaluate top 20 recipes
for i, recipe in enumerate(population[:20]):
    creativity = creativity_evaluation.evaluate_creativity(recipe, ga.recipes)
    print(f"\nRecipe {i+1}: {recipe['name']}")
    print(f"  Creativity Score: {creativity['creativity']:.3f}")
    print(f"  Novelty: {creativity['novelty']:.3f}")
    print(f"  Value: {creativity['value']:.3f}")
    print(f"  Typicality: {creativity['typicality']:.3f}")
    print(f"  Fitness: {recipe['fitness']:.3f}")

# Plot creativity vs fitness
creativities = [creativity_evaluation.evaluate_creativity(r, ga.recipes)['creativity'] for r in population[:40]]
fitnesses = [r['fitness'] for r in population[:40]]

plt.figure(figsize=(10, 6))
plt.scatter(creativities, fitnesses, alpha=0.6)
plt.xlabel("Creativity Score")
plt.ylabel("Fitness Score")
plt.title("Creativity vs Fitness in Generated Recipes")
plt.grid(True, alpha=0.3)
plt.show()

# Print best recipe
print("\n" + "="*40)
print("BEST RECIPE:")
print("="*40)
best = population[0]
print(f"Name: {best['name']}")
print(f"Fitness: {best['fitness']:.3f}")
print("\nIngredients:")
for ing in sorted(best['ingredients'], key=lambda x: ga.get_category(x['ingredient'])):
    cat = ga.get_category(ing['ingredient'])
    print(f"  [{cat:12s}] {ing['amount']:6.2f} {ing['unit']:10s} {ing['ingredient']}")