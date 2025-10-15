# Description

- recipe_output.json
  - JSON knowledgebase
- ga.py
  - Genetic algorithm for evolution
- creativity_evaluation.py
  - Customized creativity evaluation based upon
    - Novelty
    - Value
    - Typicality
- generator.py
  - Recipe generation experiments
  - `population_size` and `generations` can be modified to test with different parameters.

# How to run this repo

- Create a virtual env(conda recommended)

```bash
conda create --name G18A1 --file requirements.txt
```

- Activate virtual env

```bash
conda activate G18A1
```

- Run generator using provided JSON

```bash
python generator.py
```
