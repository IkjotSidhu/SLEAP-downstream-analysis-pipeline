# Changelog

All notable changes to the SLEAP Analysis Pipeline will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Batch processing for multiple files
- Statistical analysis and behavioral metrics
- Angular velocity calculations
- Social behavior quantification
- Machine learning-based behavior classification
- Data export to CSV/Excel formats
- GUI interface for non-programmers

### Known Issues
- None reported yet

### Roadmap
- [ ] Add interactive visualizations
- [ ] Implement batch processing
- [ ] Add statistical analysis functions
- [ ] Create GUI interface
- [ ] Add more behavioral metrics
- [ ] Improve performance for large datasets
- [ ] Add support for 3D tracking data
