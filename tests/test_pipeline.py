"""
Unit tests for the SLEAP analysis pipeline.

Run with: python -m pytest tests/
"""

import sys
from pathlib import Path
import numpy as np
import pytest
import tempfile
import h5py

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sleap_plotting import (
    AnalysisConfig, 
    fill_missing, 
    smooth_diff, 
    get_data_summary,
    validate_file_path,
    create_output_directory
)

class TestAnalysisConfig:
    """Test the AnalysisConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = AnalysisConfig()
        assert config.fps == 30
        assert config.velocity_window == 25
        assert config.velocity_poly_order == 3
        assert config.figure_format == 'pdf'
        assert config.colormap == 'plasma'
    
    def test_config_update(self):
        """Test configuration updates."""
        config = AnalysisConfig()
        config.update(fps=60, velocity_window=15)
        
        assert config.fps == 60
        assert config.velocity_window == 15
        # Other values should remain default
        assert config.velocity_poly_order == 3
    
    def test_config_invalid_parameter(self, capsys):
        """Test handling of invalid parameters."""
        config = AnalysisConfig()
        config.update(invalid_param=123)
        
        captured = capsys.readouterr()
        assert "Warning: Unknown parameter 'invalid_param' ignored" in captured.out

class TestDataProcessing:
    """Test data processing functions."""
    
    def test_fill_missing_basic(self):
        """Test basic missing data filling."""
        # Create test data with missing values
        data = np.array([[1, 2, 3], [np.nan, 5, 6], [7, 8, 9]])
        filled = fill_missing(data)
        
        # Should interpolate the missing value
        assert not np.isnan(filled).any()
        assert filled[1, 0] == 4.0  # Linear interpolation between 1 and 7
    
    def test_fill_missing_all_nan(self):
        """Test filling when entire column is NaN."""
        data = np.array([[1, np.nan], [2, np.nan], [3, np.nan]])
        filled = fill_missing(data)
        
        # First column should be unchanged, second should remain NaN
        assert np.array_equal(filled[:, 0], [1, 2, 3])
        assert np.all(np.isnan(filled[:, 1]))
    
    def test_fill_missing_insufficient_data(self):
        """Test filling with insufficient data points."""
        data = np.array([[np.nan], [1], [np.nan]])
        filled = fill_missing(data)
        
        # Should handle gracefully (only one non-NaN point)
        assert filled.shape == data.shape
    
    def test_smooth_diff_basic(self):
        """Test basic velocity calculation."""
        # Create simple trajectory data
        frames = 100
        t = np.linspace(0, 10, frames)
        x = np.sin(t)
        y = np.cos(t)
        trajectory = np.column_stack([x, y])
        
        velocity = smooth_diff(trajectory, win=25, poly=3)
        
        assert len(velocity) == frames
        assert np.all(velocity >= 0)  # Velocity magnitude should be non-negative
        assert not np.any(np.isnan(velocity))
    
    def test_smooth_diff_small_window(self, capsys):
        """Test velocity calculation with window larger than data."""
        small_data = np.array([[1, 2], [3, 4], [5, 6]])
        velocity = smooth_diff(small_data, win=25)
        
        captured = capsys.readouterr()
        assert "Warning: Window size" in captured.out
        assert len(velocity) == 3
    
    def test_smooth_diff_nan_data(self):
        """Test velocity calculation with NaN data."""
        data = np.array([[1, 2], [np.nan, np.nan], [5, 6]])
        velocity = smooth_diff(data)
        
        # Should handle NaN gracefully
        assert len(velocity) == 3

class TestUtilities:
    """Test utility functions."""
    
    def test_get_data_summary(self):
        """Test data summary generation."""
        # Create fake location data
        locations = np.random.rand(100, 5, 2, 2)  # 100 frames, 5 nodes, 2 coords, 2 instances
        locations[10:20, 0, :, :] = np.nan  # Add some missing data
        
        node_names = ['head', 'neck', 'body', 'tail', 'centroid']
        summary = get_data_summary(locations, node_names)
        
        assert summary['frame_count'] == 100
        assert summary['node_count'] == 5
        assert summary['instance_count'] == 2
        assert len(summary['node_names']) == 5
        assert summary['missing_data_percentage'] > 0
        assert summary['total_tracking_points'] == locations.size
    
    def test_validate_file_path_existing(self):
        """Test file path validation with existing file."""
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Should not raise exception
            validate_file_path(tmp_path)
        finally:
            Path(tmp_path).unlink()
    
    def test_validate_file_path_missing(self):
        """Test file path validation with missing file."""
        with pytest.raises(FileNotFoundError):
            validate_file_path("nonexistent_file.h5")
    
    def test_validate_file_path_wrong_extension(self, capsys):
        """Test file path validation with wrong extension."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            validate_file_path(tmp_path)
            captured = capsys.readouterr()
            assert "may not be a valid HDF5 file" in captured.out
        finally:
            Path(tmp_path).unlink()
    
    def test_create_output_directory(self):
        """Test output directory creation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = Path(tmp_dir) / "test_output" / "subdir"
            create_output_directory(str(test_dir))
            
            assert test_dir.exists()
            assert test_dir.is_dir()

class TestDataGeneration:
    """Test data generation for testing purposes."""
    
    @staticmethod
    def create_test_h5_file(file_path, frames=100, nodes=5, instances=2):
        """Create a test HDF5 file with SLEAP-like structure."""
        with h5py.File(file_path, 'w') as f:
            # Create tracks dataset
            tracks_shape = (frames, nodes, 2, instances)  # frames, nodes, coordinates, instances
            tracks_data = np.random.rand(*tracks_shape) * 100  # Random positions 0-100
            
            # Add some missing data
            missing_indices = np.random.choice(frames * nodes * instances, size=50, replace=False)
            tracks_flat = tracks_data.reshape(-1, 2)
            tracks_flat[missing_indices] = np.nan
            tracks_data = tracks_flat.reshape(tracks_shape)
            
            f.create_dataset('tracks', data=tracks_data)
            
            # Create node names
            node_names = [f'node_{i}'.encode() for i in range(nodes)]
            f.create_dataset('node_names', data=node_names)
        
        return tracks_data, [name.decode() for name in node_names]

@pytest.fixture
def sample_h5_file():
    """Fixture providing a sample HDF5 file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as tmp:
        tmp_path = tmp.name
    
    # Create test data
    test_data = TestDataGeneration()
    tracks_data, node_names = test_data.create_test_h5_file(tmp_path)
    
    yield tmp_path, tracks_data, node_names
    
    # Cleanup
    Path(tmp_path).unlink()

class TestIntegration:
    """Integration tests using sample data."""
    
    def test_load_sample_data(self, sample_h5_file):
        """Test loading sample HDF5 data."""
        file_path, expected_tracks, expected_nodes = sample_h5_file
        
        # This would test the load_sleap_data function
        # locations, node_names, frame_count, node_count, instance_count = load_sleap_data(file_path)
        
        # For now, just test that the file exists and is readable
        with h5py.File(file_path, 'r') as f:
            assert 'tracks' in f
            assert 'node_names' in f
            assert f['tracks'].shape[1] == len(expected_nodes)

if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__])
