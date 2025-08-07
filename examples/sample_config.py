"""
Configuration examples for the SLEAP analysis pipeline.

This file shows different ways to configure the analysis pipeline
for various experimental setups and requirements.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sleap_plotting import AnalysisConfig, plotting_SLEAP

# =============================================================================
# BASIC CONFIGURATIONS
# =============================================================================

def basic_config():
    """Basic configuration for standard analysis."""
    config = AnalysisConfig()
    # Uses default settings:
    # fps=30, velocity_window=25, velocity_poly_order=3, etc.
    return config

def high_speed_video_config():
    """Configuration for high-speed video analysis."""
    config = AnalysisConfig()
    config.update(
        fps=120,                   # High frame rate
        velocity_window=50,        # Larger smoothing window
        velocity_vmax=50,         # Higher velocity range
        figure_format='png',      # Faster to generate than PDF
    )
    return config

def low_frame_rate_config():
    """Configuration for low frame rate videos."""
    config = AnalysisConfig()
    config.update(
        fps=10,                   # Low frame rate
        velocity_window=5,        # Smaller smoothing window
        velocity_poly_order=2,    # Lower polynomial order
        velocity_vmax=10,        # Lower velocity range
    )
    return config

# =============================================================================
# SPECIALIZED CONFIGURATIONS
# =============================================================================

def publication_quality_config():
    """High-quality configuration for publication figures."""
    config = AnalysisConfig()
    config.update(
        figure_format='pdf',      # Vector graphics
        figure_dpi=600,          # High resolution
        colormap='viridis',      # Colorblind-friendly
        velocity_window=35,      # Smoother velocity traces
    )
    return config

def batch_processing_config():
    """Fast configuration for batch processing many files."""
    config = AnalysisConfig()
    config.update(
        figure_format='png',      # Faster generation
        figure_dpi=150,          # Lower resolution for speed
        velocity_window=15,      # Smaller window for speed
    )
    return config

def social_behavior_config():
    """Configuration optimized for social behavior analysis."""
    config = AnalysisConfig()
    config.update(
        fps=25,
        velocity_window=20,      # Good balance of smoothing
        velocity_vmax=15,       # Typical for social interactions
        colormap='plasma',      # Good contrast for velocity
    )
    return config

# =============================================================================
# SPECIES-SPECIFIC CONFIGURATIONS
# =============================================================================

def mouse_config():
    """Configuration optimized for mouse tracking."""
    config = AnalysisConfig()
    config.update(
        fps=30,
        velocity_window=25,
        velocity_vmax=20,       # Typical mouse velocities
        colormap='plasma',
    )
    return config

def rat_config():
    """Configuration optimized for rat tracking."""
    config = AnalysisConfig()
    config.update(
        fps=25,
        velocity_window=30,     # Larger animals, more smoothing
        velocity_vmax=25,      # Rats can move faster than mice
        colormap='viridis',
    )
    return config

def fly_config():
    """Configuration optimized for fly tracking."""
    config = AnalysisConfig()
    config.update(
        fps=60,                # Flies move fast, need higher fps
        velocity_window=15,    # Smaller window for quick movements
        velocity_vmax=100,     # Flies can have very high velocities
        colormap='hot',
    )
    return config

# =============================================================================
# EXAMPLE USAGE FUNCTIONS
# =============================================================================

def run_with_config_example():
    """Example of how to use configurations with the pipeline."""
    
    # Choose your configuration
    config = publication_quality_config()  # or any other config
    
    # File paths (update these for your data)
    file_path = "path/to/your/sleap_output.h5"
    main_node = "neck"
    output_dir = "./publication_results"
    
    # Run analysis with configuration
    try:
        results = plotting_SLEAP(
            file_path=file_path,
            main_node=main_node,
            fps=config.fps,
            output_dir=output_dir
        )
        print("✅ Analysis complete with custom configuration!")
        
    except FileNotFoundError:
        print("❌ Please update file_path with your actual data file.")

def compare_configurations():
    """Example showing how to run the same analysis with different configs."""
    
    file_path = "path/to/your/sleap_output.h5"
    main_node = "neck"
    
    # List of configurations to compare
    configs = {
        'standard': basic_config(),
        'high_quality': publication_quality_config(),
        'fast': batch_processing_config(),
        'social': social_behavior_config()
    }
    
    for config_name, config in configs.items():
        output_dir = f"./results_{config_name}"
        
        print(f"🔄 Running analysis with {config_name} configuration...")
        
        try:
            results = plotting_SLEAP(
                file_path=file_path,
                main_node=main_node,
                fps=config.fps,
                output_dir=output_dir
            )
            print(f"✅ {config_name.capitalize()} analysis complete!")
            
        except FileNotFoundError:
            print("❌ Please update file_path with your actual data file.")
            break
        except Exception as e:
            print(f"❌ Error in {config_name} analysis: {e}")

def custom_config_example():
    """Example of creating a completely custom configuration."""
    
    # Start with basic config
    config = AnalysisConfig()
    
    # Customize for your specific needs
    config.update(
        fps=45,                    # Your video frame rate
        velocity_window=20,        # Smoothing preference
        velocity_poly_order=4,     # Higher order polynomial
        velocity_vmin=0.5,        # Custom velocity range
        velocity_vmax=30,
        figure_format='svg',       # Vector graphics, smaller than PDF
        figure_dpi=300,
        colormap='coolwarm'       # Your preferred colormap
    )
    
    # Verify configuration
    print("🔧 Custom Configuration:")
    print(f"  • Frame rate: {config.fps} fps")
    print(f"  • Velocity window: {config.velocity_window}")
    print(f"  • Output format: {config.figure_format}")
    print(f"  • Colormap: {config.colormap}")
    
    return config

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def validate_config(config):
    """Validate that a configuration makes sense."""
    
    warnings = []
    
    if config.velocity_window >= 100:
        warnings.append("Very large velocity window may over-smooth data")
    
    if config.velocity_window < 5:
        warnings.append("Very small velocity window may be noisy")
    
    if config.fps > 200:
        warnings.append("Very high frame rate - ensure this is correct")
    
    if config.velocity_poly_order > config.velocity_window - 1:
        warnings.append("Polynomial order too high for window size")
    
    if warnings:
        print("⚠️  Configuration warnings:")
        for warning in warnings:
            print(f"  • {warning}")
    else:
        print("✅ Configuration looks good!")

if __name__ == "__main__":
    print("🔧 SLEAP Analysis Pipeline - Configuration Examples")
    print("=" * 60)
    
    # Show example configurations
    configs = {
        "Basic": basic_config(),
        "High-speed video": high_speed_video_config(),
        "Publication quality": publication_quality_config(),
        "Mouse tracking": mouse_config(),
        "Fly tracking": fly_config()
    }
    
    for name, config in configs.items():
        print(f"\n📋 {name} Configuration:")
        print(f"  • FPS: {config.fps}")
        print(f"  • Velocity window: {config.velocity_window}")
        print(f"  • Velocity range: {config.velocity_vmin}-{config.velocity_vmax}")
        print(f"  • Output format: {config.figure_format}")
        print(f"  • Colormap: {config.colormap}")
    
    print(f"\n🔧 Creating custom configuration...")
    custom_config = custom_config_example()
    validate_config(custom_config)
    
    print(f"\n💡 To use any configuration:")
    print(f"   config = mouse_config()  # or any other config function")
    print(f"   plotting_SLEAP(file_path, node_name, fps=config.fps)")
