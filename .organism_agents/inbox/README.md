# 📥 The Inbox (Task Entry)
This directory acts as the entry point for the OS State Bus.
Drop a `.md` payload (an `InterAgentHandshakeAtom` or trigger file) in here. 
The Orchestrator daemon actively watches this folder and will immediately dispatch it to the appropriate Organism (Agent).
