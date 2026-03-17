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


