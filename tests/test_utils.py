"""
Additional utility tests for the SLEAP analysis pipeline.
"""

import sys
from pathlib import Path
import numpy as np
import pytest

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sleap_plotting import AnalysisConfig

class TestMathUtils:
    """Test mathematical utility functions."""
    
    def test_velocity_calculation_consistency(self):
        """Test that velocity calculations are consistent."""
        # Create known trajectory
        t = np.linspace(0, 2*np.pi, 100)
        radius = 10
        x = radius * np.cos(t)
        y = radius * np.sin(t)
        trajectory = np.column_stack([x, y])
        
        from sleap_plotting import smooth_diff
        
        # Test with different window sizes
        velocities = []
        for win in [15, 25, 35]:
            if win < len(trajectory):
                vel = smooth_diff(trajectory, win=win)
                velocities.append(vel)
        
        # All velocity calculations should have same length
        lengths = [len(v) for v in velocities]
        assert all(l == lengths[0] for l in lengths)
        
        # For circular motion, velocity should be roughly constant
        for vel in velocities:
            cv = np.std(vel) / np.mean(vel)  # Coefficient of variation
            assert cv < 0.5  # Should be relatively consistent
    
    def test_distance_calculation(self):
        """Test distance calculations."""
        # Create two simple trajectories
        traj1 = np.array([[0, 0], [1, 0], [2, 0]])  # Moving right
        traj2 = np.array([[0, 3], [1, 3], [2, 3]])  # Moving right, 3 units up
        
        # Distance should always be 3
        distances = np.linalg.norm(traj1 - traj2, axis=1)
        expected = np.array([3, 3, 3])
        
        np.testing.assert_array_almost_equal(distances, expected)
    
    def test_cumulative_distance(self):
        """Test cumulative distance calculation."""
        # Simple trajectory: move 1 unit right each frame
        trajectory = np.array([[0, 0], [1, 0], [2, 0], [3, 0]])
        
        # Calculate frame-to-frame distances
        diffs = np.diff(trajectory, axis=0)
        distances = np.linalg.norm(diffs, axis=1)
        
        # Each step should be 1 unit
        expected_distances = np.array([1, 1, 1])
        np.testing.assert_array_almost_equal(distances, expected_distances)
        
        # Cumulative distance
        cumulative = np.cumsum(distances)
        expected_cumulative = np.array([1, 2, 3])
        np.testing.assert_array_almost_equal(cumulative, expected_cumulative)

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_data(self):
        """Test handling of empty data."""
        from sleap_plotting import fill_missing
        
        # Empty array
        empty_data = np.array([]).reshape(0, 2)
        result = fill_missing(empty_data)
        assert result.shape == empty_data.shape
    
    def test_single_frame(self):
        """Test handling of single frame data."""
        from sleap_plotting import smooth_diff
        
        single_frame = np.array([[1, 2]])
        
        # Should handle gracefully without crashing
        try:
            velocity = smooth_diff(single_frame, win=5)
            assert len(velocity) == 1
        except Exception as e:
            pytest.fail(f"Single frame handling failed: {e}")
    
    def test_all_nan_trajectory(self):
        """Test handling of all-NaN trajectory."""
        from sleap_plotting import smooth_diff
        
        nan_trajectory = np.full((10, 2), np.nan)
        velocity = smooth_diff(nan_trajectory)
        
        # Should return array of appropriate length
        assert len(velocity) == 10
        # Result may be NaN or zeros, but shouldn't crash

class TestConfigValidation:
    """Test configuration parameter validation."""
    
    def test_config_bounds(self):
        """Test configuration parameter bounds."""
        config = AnalysisConfig()
        
        # Test reasonable bounds
        assert config.fps > 0
        assert config.velocity_window > 0
        assert config.velocity_poly_order > 0
        assert config.velocity_vmin >= 0
        assert config.velocity_vmax > config.velocity_vmin
        assert config.figure_dpi > 0
    
    def test_config_types(self):
        """Test configuration parameter types."""
        config = AnalysisConfig()
        
        assert isinstance(config.fps, (int, float))
        assert isinstance(config.velocity_window, int)
        assert isinstance(config.velocity_poly_order, int)
        assert isinstance(config.figure_format, str)
        assert isinstance(config.colormap, str)
    
    def test_config_string_values(self):
        """Test valid string configuration values."""
        config = AnalysisConfig()
        
        # Test valid figure formats
        valid_formats = ['pdf', 'png', 'svg', 'jpg', 'eps']
        for fmt in valid_formats:
            config.update(figure_format=fmt)
            assert config.figure_format == fmt
        
        # Test valid colormaps (just a few common ones)
        valid_cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'hot', 'cool']
        for cmap in valid_cmaps:
            config.update(colormap=cmap)
            assert config.colormap == cmap

class TestNumericalStability:
    """Test numerical stability of calculations."""
    
    def test_large_coordinates(self):
        """Test handling of large coordinate values."""
        from sleap_plotting import smooth_diff
        
        # Large coordinate values
        large_coords = np.array([[1e6, 1e6], [1e6 + 1, 1e6 + 1], [1e6 + 2, 1e6 + 2]])
        
        velocity = smooth_diff(large_coords, win=3)
        
        # Should not produce NaN or infinite values
        assert np.all(np.isfinite(velocity))
        assert np.all(velocity >= 0)  # Velocity magnitude should be non-negative
    
    def test_small_movements(self):
        """Test handling of very small movements."""
        from sleap_plotting import smooth_diff
        
        # Very small movements
        small_movements = np.array([[0, 0], [1e-10, 1e-10], [2e-10, 2e-10]])
        
        velocity = smooth_diff(small_movements, win=3)
        
        # Should handle small numbers without issues
        assert np.all(np.isfinite(velocity))
        assert np.all(velocity >= 0)
    
    def test_zero_movement(self):
        """Test handling of zero movement (stationary animal)."""
        from sleap_plotting import smooth_diff
        
        # No movement
        stationary = np.array([[5, 5], [5, 5], [5, 5], [5, 5]])
        
        velocity = smooth_diff(stationary, win=3)
        
        # Velocity should be zero or very close to zero
        assert np.all(velocity < 1e-10)

if __name__ == "__main__":
    pytest.main([__file__])
