#!/usr/bin/env python3
"""
Example script demonstrating the SLEAP analysis pipeline.

This script shows how to:
1. Configure analysis parameters
2. Run the complete pipeline
3. Access and use the results

Replace the file_path and main_node with your actual data.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import sleap_plotting
sys.path.append(str(Path(__file__).parent.parent))

from sleap_plotting import plotting_SLEAP, AnalysisConfig, load_sleap_data

def main():
    """Run example analysis with sample configuration."""
    
    # =============================================================================
    # CONFIGURATION - Modify these parameters for your data
    # =============================================================================
    
    # Path to your SLEAP HDF5 output file
    file_path = ''  # CHANGE THIS
    
    # Node of interest (must match a node name in your SLEAP model)
    main_node = "bodycenter"  # CHANGE THIS - options might include: head, bodycenter, thorax, etc.
    
    # Analysis parameters
    fps = 30  # Frame rate of your video
    output_dir = "./example_results"
    
    # =============================================================================
    # ADVANCED CONFIGURATION
    # =============================================================================
    
    # Create configuration object with custom parameters
    config = AnalysisConfig()
    config.update(
        fps=fps,
        velocity_window=25,         # Window size for velocity smoothing
        velocity_poly_order=3,      # Polynomial order for Savitzky-Golay filter
        velocity_vmin=0,           # Minimum value for velocity plots
        velocity_vmax=20,          # Maximum value for velocity plots
        figure_format='pdf',       # Output format: 'pdf', 'png', 'svg'
        figure_dpi=300,           # Figure resolution
        colormap='plasma'         # Colormap for velocity plots
    )
    
    # =============================================================================
    # CHECK DATA AVAILABILITY
    # =============================================================================
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {file_path}")
        print("Please update the file_path variable with your SLEAP output file.")
        print("\nExample SLEAP file structure:")
        print("- your_experiment.h5")
        print("  ├── tracks (frames, nodes, coordinates, instances)")
        print("  └── node_names")
        return
    
    # =============================================================================
    # RUN ANALYSIS PIPELINE
    # =============================================================================
    
    print("🚀 Starting SLEAP analysis pipeline...")
    print(f"📁 Input file: {file_path}")
    print(f"🎯 Target node: {main_node}")
    print(f"📊 Frame rate: {fps} fps")
    print(f"📁 Output directory: {output_dir}")
    print("-" * 50)
    
    try:
        # Run the complete analysis pipeline
        results = plotting_SLEAP(
            file_path=file_path,
            main_node=main_node,
            fps=config.fps,
            output_dir=output_dir
        )
        
        print("\n✅ Analysis completed successfully!")
        print(f"📁 Results saved to: {output_dir}")
        
        # =============================================================================
        # DISPLAY RESULTS SUMMARY
        # =============================================================================
        
        summary = results['summary']
        print("\n📊 ANALYSIS SUMMARY:")
        print(f"  • Total frames: {summary['frame_count']:,}")
        print(f"  • Nodes tracked: {summary['node_count']}")
        print(f"  • Animals: {summary['instance_count']}")
        print(f"  • Missing data: {summary['missing_data_percentage']:.2f}%")
        print(f"  • Total tracking points: {summary['total_tracking_points']:,}")
        
        print(f"\n📝 Available nodes: {', '.join(summary['node_names'])}")
        
        # =============================================================================
        # ACCESS ANALYSIS RESULTS
        # =============================================================================
        
        # Access specific results
        inter_mouse_distance = results['inter_mouse_distance']
        velocities = results['velocities']
        
        print(f"\n📏 Inter-mouse distance statistics:")
        print(f"  • Mean distance: {inter_mouse_distance.mean():.2f} pixels")
        print(f"  • Max distance: {inter_mouse_distance.max():.2f} pixels")
        print(f"  • Min distance: {inter_mouse_distance.min():.2f} pixels")
        
        print(f"\n⚡ Velocity statistics:")
        print(f"  • Mouse 1 mean velocity: {velocities['mouse1'].mean():.2f} pixels/frame")
        print(f"  • Mouse 2 mean velocity: {velocities['mouse2'].mean():.2f} pixels/frame")
        
        print(f"\n🎨 Generated plots:")
        output_path = Path(output_dir)
        if output_path.exists():
            pdf_files = list(output_path.glob("*.pdf"))
            for pdf_file in sorted(pdf_files):
                print(f"  • {pdf_file.name}")
        
        print(f"\n🎉 Pipeline completed! Check {output_dir} for all generated plots.")
        
    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
        print("Please check your file path and ensure the HDF5 file exists.")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your node name and ensure it exists in the SLEAP data.")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check your data format and try again.")

def demonstrate_individual_functions():
    """Demonstrate how to use individual analysis functions."""
    
    file_path = "path/to/your/sleap_output.h5"  # CHANGE THIS
    
    if not os.path.exists(file_path):
        print("❌ Please update the file path to run individual function examples.")
        return
    
    print("\n🔧 DEMONSTRATING INDIVIDUAL FUNCTIONS:")
    print("-" * 50)
    
    try:
        # Load data first
        print("📥 Loading SLEAP data...")
        locations, node_names, frame_count, node_count, instance_count = load_sleap_data(file_path)
        
        print(f"✅ Data loaded: {frame_count} frames, {node_count} nodes, {instance_count} instances")
        
        # Example: analyze specific node
        if "neck" in node_names:
            node_index = node_names.index("neck")
            
            print("\n📊 Running individual analyses...")
            
            # You can run specific functions like this:
            # plot_node_trajectories(locations, node_index, "neck", "./individual_results")
            # distances = analyze_inter_mouse_distance(locations, node_index, "neck")
            # velocities = analyze_velocities(locations, node_index, "neck")
            
            print("✅ Individual function examples complete.")
        else:
            print("⚠️  'neck' node not found. Available nodes:", node_names)
            
    except Exception as e:
        print(f"❌ Error in individual function demo: {e}")

if __name__ == "__main__":
    main()
    
    # Uncomment to run individual function examples
    # demonstrate_individual_functions()
