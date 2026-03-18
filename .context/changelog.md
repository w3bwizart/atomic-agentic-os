# Changelog

## [Current Phase]
### Added
- Created `.context/roadmap.json` to clearly define Phase 1 (Core OS Hardening) and Phase 2 (Agentic UI Widgets).
- Defined Phase 1 objectives to ensure rock-solid reliability of the Orchestrator, Factory, and Scaffolder prior to UI work.

### Changed
- Reprioritized development focus purely onto the Core OS. Deferred Agentic UI development.
- Updated `.context/blueprint.md` task directive to reflect the completion of Phase 1 as the absolute priority.

## [Phase 1 in_progress]
### Fixed
- Fixed silent orchestrator startup failure by configuring `PYTHONPATH=.` natively.
- Fixed duplicate `watchdog` events causing duplicate logic execution via explicit thread debouncing and size verification.
- Fixed missing `task_decomposition` execution warnings by removing unimplemented skill from Dictator configuration.



## [Completed] - Phase 1: Engine Re-Architecture
- Received Master Context Injection detailing the "V8 of AI Agents" vision.
- Pivot from basic file-watching to strict `InterAgentHandshake` state bus and heavily commented ISO-ready `runner.py` execution.
- **Implemented:** The V8 Engine architecture, the `InterAgentHandshake` Pydantic schema, the ISO-compliant Flight Recorder logging, and the `Mailroom` routing skill.
- Successfully passed all V8 testing suites and merged the core ecosystem overhauls. Phase 1 is officially complete.
