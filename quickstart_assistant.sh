#!/bin/bash

# Quickstart - skips model selection and mode prompt
# Still asks for audio device (to avoid full duplex issues)

cd /home/marco/Work/ai/llm/assistmint
source venv/bin/activate

# Usage: ./quickstart_assistant.sh [device_index] [--no-commands]
# Example: ./quickstart_assistant.sh 2
# Example: ./quickstart_assistant.sh 2 --no-commands

if [ -n "$1" ]; then
    python main.py --model mistral:latest --device "$1" --voice $2
else
    python main.py --model mistral:latest --voice
fi

deactivate
