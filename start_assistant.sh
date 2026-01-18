#!/bin/bash
# ============================================================================
# Assistmint Voice Assistant - Start Script
# ============================================================================
#
# USAGE EXAMPLES:
#   ./start_assistant.sh                    # Interactive menu
#
# DIRECT COMMANDS (bypass menu):
#   python main_modular.py --voice          # Voice mode with defaults
#   python main_modular.py --type           # Text/type mode
#
# MODEL OPTIONS:
#   --model MODEL           English model (default: qwen2.5:3b)
#   --model-nl MODEL        Dutch model (default: fietje:latest)
#   --no-auto-switch        Disable auto language switching
#
# EXAMPLES:
#   # Auto-switch between EN/NL models:
#   python main_modular.py --voice --model qwen2.5:3b --model-nl fietje:latest
#
#   # Only English (Qwen understands Dutch, responds English):
#   python main_modular.py --voice --model qwen2.5:7b --no-auto-switch
#
#   # Only Dutch:
#   python main_modular.py --voice --model fietje:latest --no-auto-switch
#
# AVAILABLE MODELS (VRAM usage):
#   qwen2.5:3b      1.9 GB   Fast, good multilingual
#   qwen2.5:7b      4.7 GB   Better quality
#   fietje:latest   5.6 GB   Dutch specialized
#   deepseek-r1:8b  5.2 GB   Reasoning model
#
# RECOMMENDED COMBOS (8GB GPU + Whisper medium ~2.5GB):
#   qwen2.5:3b + Whisper medium  = ~4.5 GB (safe)
#   qwen2.5:7b + Whisper medium  = ~7.2 GB (tight)
#   fietje + Whisper medium      = ~8.1 GB (max)
#
# ============================================================================

# Clean GPU before start
echo "🧹 Cleaning GPU before start..."
./kill-gpu-python.sh --force
echo ""

read -p "Welke wil je starten: jarvis of jarvis 2: " value

#jobautomation/OpenEuroLLM-Dutch:latest    32f328c86c05    8.1 GB    13 hours ago
#codellama:7b                              8fdf8f752f6e    3.8 GB    24 hours ago
#deepseek-coder:6.7b                       ce298d984115    3.8 GB    24 hours ago
#qwen2.5-coder:7b                          dae161e27b0e    4.7 GB    24 hours ago
#qwen2.5:7b                                845dbda0ea48    4.7 GB    25 hours ago
#qwen2.5:3b                                357c53fb659c    1.9 GB    25 hours ago
#fietje:latest                             80881d74bad6    5.6 GB    27 hours ago
#bramvanroy/fietje-2b-chat:f16             80881d74bad6    5.6 GB    27 hours ago
#saul:latest                               c78f2b26f1ef    4.4 GB    35 hours ago
#mistral:latest                            6577803aa9a0    4.4 GB    37 hours ago
#llama2:latest                             78e26419b446    3.8 GB    3 days ago
#qwen2.5:0.5b                              a8b0c5157701    397 MB    3 days ago
#deepseek-r1:8b                            6995872bfe4c    5.2 GB    3 weeks ago
#deepseek-r1:1.5b                          e0979632db5a    1.1 GB    3 weeks ago
# Navigate to the project directory
cd /home/marco/Work/ai/llm/assistmint

# Activate the virtual environment
source venv/bin/activate
#if $value = super
#then python3.12 main_modular.py --model qwen2.5:7b --voice --no-commands --device 2
#else python3.12 main.py --model qwen2.5:7b --voice --no-commands --device 2
#continue
# Set CUDA library path for GPU support (CUDA 12)
# Check venv first, then ~/.local as fallback
if [ -d "$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia" ]; then
    NVIDIA_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia"
else
    NVIDIA_PATH="$HOME/.local/lib/python3.12/site-packages/nvidia"
fi
export LD_LIBRARY_PATH="$NVIDIA_PATH/cuda_runtime/lib:$NVIDIA_PATH/cublas/lib:$NVIDIA_PATH/cudnn/lib:$NVIDIA_PATH/cufft/lib:$LD_LIBRARY_PATH"

# Run the main.py script
pip install -r requirements.txt
#python3.12 main_modular.py --model qwen2.5:7b --voice --no-commands --device 2

if [ $value = "jarvis" ]; then
echo "jarvis 1 starting......"
python main.py --model qwen2.5:7b --voice --no-commands --device 2
else
echo "Jarvis 2 starting...."
  python main_modular.py --voice --model qwen2.5:3b --model-nl bramvanroy/fietje-2b-chat:q4_K_M --no-commands --device 3              

#python main_modular.py --model qwen2.5:3b --voice --no-commands --device 2
fi


#python main_modular.py --model qwen2.5:7b --voice --no-commands --device 2

#python main.py --model qwen2.5:7b --voice --no-commands --device 2
# python main.py --model llama2:latest --device 2 --voice --no-commands


# Deactivate the virtual environment after the script ends
deactivate

# Clean GPU after exit
echo ""
echo "🧹 Cleaning GPU after exit..."
./kill-gpu-python.sh --force
