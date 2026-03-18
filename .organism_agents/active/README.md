# ⚙️ Active Processing (Flight Recorders)
This directory temporarily holds `.state.json` files while an Organism is actively thinking.
These act as black-box flight recorders, capturing exact timestamps, LLM traces, and crash faults in real-time. 
Once a task completes (Success or Fail), the State Bus moves the final output to the `review/` folder.
