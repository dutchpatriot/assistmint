#!/bin/bash

# Navigate to the project directory
cd /home/marco/Work/ai/llm/assistmint

# Activate the virtual environment
source venv/bin/activate

# Run the main.py script
python main.py --model mistral:latest --device 2 --voice --no-commands


# Deactivate the virtual environment after the script ends
deactivate
