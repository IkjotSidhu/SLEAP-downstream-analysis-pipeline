# SLEAP Analysis Pipeline
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# - Per-second aggregated CSV files (*_by_seconds.csv)
# - Per-minute aggregated CSV files (*_by_minutes.csv)
# - Publication-ready PDF visualizations
```

### Advanced Configuration

```python
from sleap_plotting import *

# Customize analysis parameters
config = AnalysisConfig()
config.update(
    fps=25,                     # Frame rate
    velocity_window=15,         # Smoothing window
    velocity_poly_order=3,      # Polynomial order
    figure_format='png',        # Output format
    colormap='viridis'          # Color scheme
)

# Run analysis with custom config
results = plotting_SLEAP(
    file_path="data.h5",
    main_node="bodycenter",
    fps=config.fps,
    output_dir="./custom_analysis"
)
```

### Individual Analysis Functions

```python
# Load data first
locations, node_names, frame_count, node_count, instance_count = load_sleap_data("data.h5")

# Run specific analyses (now with time-based CSV exports)
plot_node_trajectories(locations, node_index=0, node_name="bodycenter", fps=30)
distances = analyze_inter_mouse_distance(locations, node_index=0, node_name="bodycenter", fps=30)
velocities = analyze_velocities(locations, node_index=0, node_name="bodycenter", fps=30)
analyze_cumulative_distance(locations, node_index=0, node_name="bodycenter", fps=30)

# Each function now generates:
# - Original detailed CSV with time information
# - Per-second aggregated CSV (*_by_seconds.csv)
# - Per-minute aggregated CSV (*_by_minutes.csv)
```

## 📁 Repository Structure

```
sleap-analysis-pipeline/
├── sleap_plotting.py          # Main analysis pipeline
├── requirements.txt           # Python dependencies  
├── README.md                 # This file
├── .gitignore               # Git ignore rules
├── examples/                # Example scripts and data
│   ├── example_analysis.py  # Complete example
│   └── sample_config.py     # Configuration examples
├── docs/                    # Documentation
│   ├── API.md              # API reference
│   └── examples.md         # Usage examples
└── tests/                   # Unit tests
    ├── test_pipeline.py    # Pipeline tests
    └── test_utils.py       # Utility tests
```

## 📊 Output Files

The pipeline generates both visualizations (PDF) and data files (CSV) for further analysis:

### PDF Visualizations
| File | Description |
|------|-------------|
| `{node}_locations.pdf` | Time-series position plots |
| `{node}_Node-Mouse-Tracking-plot.pdf` | Spatial trajectory plots |
| `{node}_Inter-Mouse-Distance-by-Frame.pdf` | Distance plots by frame |
| `{node}_Inter-Mouse-Distance-by-second.pdf` | Distance plots by time |
| `Mouse-1-{node}-velocity-plot.pdf` | Velocity analysis for animal 1 |
| `Mouse-2-{node}-velocity-plot.pdf` | Velocity analysis for animal 2 |
| `Cumulative-distance-over-time-{node}.pdf` | Cumulative movement analysis |

### CSV Data Files

The pipeline generates comprehensive CSV outputs at multiple temporal resolutions:

#### Frame-by-Frame Data (Original + Enhanced)
| File | Description | Columns |
|------|-------------|---------|
| `{node}_trajectories.csv` | Raw position data with time | frame, time_seconds, mouse1_x, mouse1_y, mouse2_x, mouse2_y |
| `{node}_inter_mouse_distances.csv` | Distance measurements with time | frame, time_seconds, inter_mouse_distance_pixels, mouse1_x, mouse1_y, mouse2_x, mouse2_y |
| `{node}_velocities.csv` | Velocity calculations with time | frame, time_seconds, mouse1_velocity_pixels_per_frame, mouse2_velocity_pixels_per_frame, mouse1_velocity_pixels_per_second, mouse2_velocity_pixels_per_second, positions |
| `{node}_cumulative_distances.csv` | Movement statistics with time | frame, time_seconds, mouse1_frame_distance, mouse1_cumulative_distance, mouse2_frame_distance, mouse2_cumulative_distance |

#### Time-Aggregated Data (NEW! 🆕)

**Per-Second Aggregation:**
| File | Description | Statistical Measures |
|------|-------------|---------------------|
| `{node}_trajectories_by_seconds.csv` | Average positions per second | mean positions for each mouse |
| `{node}_inter_mouse_distances_by_seconds.csv` | Distance statistics per second | mean, std, min, max, count + average positions |
| `{node}_velocities_by_seconds.csv` | Velocity statistics per second | mean, std, min, max for velocities + average positions |
| `{node}_cumulative_distances_by_seconds.csv` | Distance metrics per second | sum, mean, count of frame distances + final cumulative values |

**Per-Minute Aggregation:**
| File | Description | Statistical Measures |
|------|-------------|---------------------|
| `{node}_trajectories_by_minutes.csv` | Average positions per minute | mean positions for each mouse |
| `{node}_inter_mouse_distances_by_minutes.csv` | Distance statistics per minute | mean, std, min, max, count + average positions |
| `{node}_velocities_by_minutes.csv` | Velocity statistics per minute | mean, std, min, max for velocities + average positions |
| `{node}_cumulative_distances_by_minutes.csv` | Distance metrics per minute | sum, mean, count of frame distances + final cumulative values |

## ⏰ Time-Based Analysis Benefits

The new time-aggregated CSV exports provide several advantages:

### 🚀 **Performance Benefits**
- **Reduced file sizes**: Aggregated data is much smaller than frame-by-frame data
- **Faster processing**: Pre-computed statistics save analysis time
- **Memory efficiency**: Easier to work with large datasets

### 📊 **Analysis Flexibility**
- **Multiple time scales**: Choose frame-level, second-level, or minute-level resolution
- **Statistical summaries**: Built-in mean, std, min, max, and count statistics
- **Temporal patterns**: Better suited for identifying behavioral patterns over time

### 🎯 **Use Cases**
- **Long recordings**: Analyze hours of data without memory issues
- **Comparative studies**: Compare behavior across different time periods
- **Statistical analysis**: Ready-made data for statistical software (R, SPSS, etc.)
- **Visualization**: Create cleaner time-series plots with reduced noise
- **Behavioral segmentation**: Identify active vs. inactive periods

### 📈 **Example Applications**
```python
# Quick analysis of hourly activity patterns
import pandas as pd

# Load minute-aggregated data
minute_data = pd.read_csv("bodycenter_velocities_by_minutes.csv")

# Calculate hourly activity levels
minute_data['hour'] = minute_data['time_minutes'] // 60
hourly_activity = minute_data.groupby('hour')['mouse1_velocity_pixels_per_second_mean'].mean()

print("Average velocity by hour:")
print(hourly_activity)
```

## 🔧 Configuration Options

The `AnalysisConfig` class provides easy customization:

```python
config = AnalysisConfig()
config.fps = 25                      # Frame rate (Hz)
config.velocity_window = 15          # Smoothing window size  
config.velocity_poly_order = 3       # Polynomial order for smoothing
config.velocity_vmin = 0             # Velocity plot minimum
config.velocity_vmax = 20            # Velocity plot maximum
config.figure_format = 'png'         # Output format ('pdf', 'png', 'svg')
config.figure_dpi = 300              # Figure resolution
config.colormap = 'viridis'          # Matplotlib colormap
```

## 📋 Data Requirements

The pipeline expects HDF5 files from SLEAP with:
- `tracks`: 4D array of shape `(frames, nodes, coordinates, instances)`
- `node_names`: List of node/keypoint names

## 🎯 Best Practices

### Data Preparation
- Ensure SLEAP predictions are of good quality before analysis
- Choose stable, well-tracked nodes (e.g., "bodycenter", "centroid") as primary nodes
- Verify frame rate settings match your video data

### Analysis Tips
- Use appropriate velocity smoothing windows (30+ frames typical)
- Check missing data percentage before analysis
- Save intermediate results for large datasets
- **NEW**: Use time-aggregated CSV files (*_by_seconds.csv, *_by_minutes.csv) for faster analysis of long recordings
- **NEW**: Choose appropriate temporal resolution: frame-level for detailed analysis, second/minute-level for behavioral patterns

### Troubleshooting
- **Import Errors**: Verify all dependencies are installed
- **File Not Found**: Check file paths and HDF5 file accessibility  
- **Node Not Found**: Confirm node names match your SLEAP model
- **Memory Issues**: Consider analyzing shorter segments for large datasets

## 🧪 Testing

Run the test suite to verify installation:

```bash
python -m pytest tests/
```


## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Citation

If you use this pipeline in your research, please cite:

```bibtex
@software{sleap_analysis_pipeline,
  title={SLEAP Analysis Pipeline},
  author=Ikjot Sidhu,
  year={2025},
  url={https://github.com/IkjotSidhu/SLEAP-downstream-analysis-pipeline}
}
```

## 🙏 Acknowledgments

- [SLEAP Team](https://sleap.ai/) for the excellent pose estimation framework
- Scientific Python community for the foundational libraries
- Contributors and users who provide feedback and improvements

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/IkjotSidhu/SLEAP-downstream-analysis-pipeline/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/IkjotSidhu/SLEAP-downstream-analysis-pipeline/discussions)
- **Documentation**: Check the [docs/](docs/) folder for detailed guides

---

**⭐ Star this repository if you find it helpful!**
