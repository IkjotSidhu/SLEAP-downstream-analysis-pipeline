# Changelog

All notable changes to the SLEAP Analysis Pipeline will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-05-05

### Added
- **Time-aggregated CSV exports**: every analysis function now produces per-second (`*_by_seconds.csv`) and per-minute (`*_by_minutes.csv`) output files in addition to frame-level CSVs
- **Pixel-to-centimetre conversion**: `calculate_pixel_to_cm_conversion()` infers a px → cm scale factor from arena dimensions
- **Multi-recording support**: `multi_recording_project/` workflow enables batch analysis across multiple sessions
- **Temporal analysis example**: `examples/temporal_analysis_example.py` demonstrates efficient use of aggregated CSV files
- Time columns (`time_seconds`) added to all frame-level CSV outputs

### Changed
- Default `colormap` changed from `viridis` to `plasma` for better velocity contrast
- README completely rewritten: cleaner structure, Table of Contents, accurate configuration defaults
- `setup.py` version updated to `1.1.0`

### Fixed
- `test_validate_file_path_wrong_extension` now correctly expects `ValueError` instead of a printed warning

---

## [1.0.0] - 2025-08-07

### Added
- Initial release of SLEAP Analysis Pipeline
- Complete analysis pipeline for SLEAP tracking data
- Modular functions for different analysis types:
  - Trajectory plotting and visualization
  - Inter-animal distance analysis
  - Velocity profile calculation with Savitzky-Golay smoothing
  - Cumulative distance traveled analysis
- Configuration system with `AnalysisConfig` class
- Robust error handling and data validation
- Missing data interpolation with multiple methods
- Publication-quality plot generation
- Comprehensive documentation and examples
- Unit test suite with pytest
- Example scripts and configuration templates

### Features
- **Data Loading**: Automatic HDF5 file loading with data validation
- **Preprocessing**: Missing data interpolation and quality assessment
- **Trajectory Analysis**: Time-series and spatial trajectory visualization
- **Distance Metrics**: Inter-animal distance calculation and plotting
- **Velocity Analysis**: Smoothed velocity profiles with customizable parameters
- **Movement Statistics**: Cumulative distance and movement patterns
- **Visualization**: High-quality plots with consistent styling
- **Configuration**: Flexible parameter system for different experimental setups
- **Error Handling**: Graceful handling of common data issues
- **Testing**: Comprehensive test suite for reliability

### Documentation
- Detailed README with installation and usage instructions
- API documentation with function descriptions
- Configuration examples for different experimental setups
- Troubleshooting guide and best practices
- Example scripts for common use cases

### Technical Details
- Python 3.7+ compatibility
- Dependencies: numpy, scipy, matplotlib, seaborn, h5py, sleap
- Modular architecture for easy extension
- Type hints and comprehensive docstrings
- Cross-platform compatibility (Windows, macOS, Linux)

## [Unreleased]

### Planned Features
- Interactive visualization with Plotly/Bokeh
- Angular velocity calculations
- Social behavior quantification metrics
- Machine learning-based behavior classification
- GUI interface for non-programmers
- Support for 3D tracking data

### Roadmap
- [ ] Add interactive visualizations
- [ ] Add angular velocity calculations
- [ ] Add social behavior quantification metrics
- [ ] Create GUI interface
- [ ] Add support for 3D tracking data
- [ ] Improve performance for very large datasets (>10 h)
