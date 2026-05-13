# CHANGELOG

## [Unreleased]
### Added
- Support for both `rpicam-vid` (Raspberry Pi OS Trixie) and `libcamera-vid` (Raspberry Pi OS Bookworm) camera commands in `src/ac_training_lab/picam/device.py` to ensure compatibility across different OS versions.
- Comprehensive Unit Operations section in `docs/index.md` documenting all available capabilities including dispensing, synthesis, characterization, and robotics operations.
- Expanded Training Workflows section in `docs/index.md` with 10 educational workflows including RGB/RYB color matching, titration, yeast growth optimization, vision-enabled 3D printing optimization, microscopy image stitching, and AprilTag robot path planning.
- Research Workflows section in `docs/index.md` documenting alkaline catalysis lifecycle testing and battery slurry viscosity optimization.
- Direct links from unit operations and workflows to relevant code locations in the repository for easier navigation.
- Resolution setting in `my_secrets_example.py` for YouTube-compatible streaming (144p, 240p, 360p, 480p, 720p, 1080p).
- Camera rotation setting (0, 90, 180, 270 degrees) for portrait mode streaming in `my_secrets_example.py`.
- Frame rate setting in `my_secrets_example.py` for adjustable stream frame rate.
- Timestamp overlay setting in `my_secrets_example.py` to display date/time (format: YYYY-MM-DD_HH-MM-SS) on video stream.

### Fixed
- Ctrl+C interrupt handling in `src/ac_training_lab/picam/device.py` now properly exits the streaming loop instead of restarting.
- Fixed typo "reagants" → "reagents" in Conductivity workflow description.

### Changed
- Removed CLI/argparse code from `device.py`; resolution and rotation are now configured via `my_secrets.py`.

## [1.1.0] - 2024-06-11
### Added
- Imperial (10-32 thread) alternative design to SEM door automation bill of materials in `docs/sem-door-automation-components.md`.
- Validated McMaster-Carr part numbers and direct links for all imperial components.

### Changed
- No changes to metric design section.

### Notes
- All components sourced from McMaster-Carr for reliability and reproducibility.
