#!/bin/bash
# Kill Python processes using GPU VRAM (for cleaning up stuck instances)
# Usage: ./kill-gpu-python.sh [--force|-y]

FORCE=false
if [[ "$1" == "--force" || "$1" == "-y" ]]; then
    FORCE=true
fi

echo "=== GPU Memory Status ==="
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader 2>/dev/null || { echo "nvidia-smi not available"; exit 0; }

echo ""
echo "=== Python processes on GPU ==="
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader 2>/dev/null | grep -i python

PIDS=$(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader 2>/dev/null | grep -i python | cut -d',' -f1 | tr -d ' ')

if [ -z "$PIDS" ]; then
    echo "No Python processes found on GPU. ✓"
    exit 0
fi

echo ""
echo "Found PIDs: $PIDS"

if [ "$FORCE" = true ]; then
    confirm="y"
else
    read -p "Kill these processes? (y/N): " confirm
fi

if [[ "$confirm" =~ ^[Yy]$ ]]; then
    for pid in $PIDS; do
        echo "Killing PID $pid..."
        kill -9 $pid 2>/dev/null
    done
    sleep 1
    echo ""
    echo "=== GPU Memory After ==="
    nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
    echo "GPU cleaned! ✓"
else
    echo "Cancelled."
fi
