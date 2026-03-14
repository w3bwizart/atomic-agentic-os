#!/usr/bin/env bash

# Zombie Protection
echo "Sweeping for zombie orchestrator processes..."
pkill -f "python3 core/orchestrator.py" || true
echo "Clean sweep complete."
