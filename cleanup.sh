#!/usr/bin/env bash

# Zombie Protection (Clean Boot Flag)
echo "Sweeping for zombie orchestrator processes in $(pwd)..."
for pid in $(pgrep -f "python3 core/orchestrator.py"); do
    if [ "$(readlink /proc/$pid/cwd 2>/dev/null)" = "$(pwd)" ]; then
        kill -9 $pid 2>/dev/null || true
    fi
done
echo "Clean sweep complete."
