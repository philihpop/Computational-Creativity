# Setup Instructions

## Installation

```bash
# Create a new conda environment
conda create -n poetry-gen python=3.10
conda activate poetry-gen

# Install PyTorch (with CUDA support if you have a GPU)
# For CUDA 11.8:
conda install pytorch pytorch-cuda=11.8 -c pytorch -c nvidia

# For CPU only:
# conda install pytorch cpuonly -c pytorch

# Install other dependencies
pip install -r requirements.txt
```

## Project Structure

Before running the notebook the project structure is:

```
.
├── romantic_poem_generator.ipynb  # Main Jupyter notebook
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── romantic/                      # Inspiring set
    ├── RomanticPoemsAFunOfRomanticPleasurePoembyRameshTA.txt
    ├── RomanticPoemsAHillWalkingPoemPartTwoTheRomanticPoetPoembyDanielBrick.txt
    └── ...
```

## Usage Instructions

### 1. Launch Jupyter Notebook

```bash
# Activate your environment first (conda or venv)
conda activate poetry-gen

# Start Jupyter
jupyter notebook
```

### 2. Run the Notebook

1. Open `romantic_poem_generator.ipynb` in Jupyter
2. Run cells sequentially from top to bottom
