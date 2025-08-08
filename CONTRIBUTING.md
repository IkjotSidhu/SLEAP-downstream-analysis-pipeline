# Contributing to SLEAP Analysis Pipeline

Thank you for your interest in contributing to the SLEAP Analysis Pipeline! This document provides guidelines for contributing to the project.

## 🤝 Ways to Contribute

### 1. Reporting Issues
- **Bug Reports**: Found a bug? Please open an issue with:
  - Clear description of the problem
  - Steps to reproduce
  - Expected vs actual behavior
  - System information (OS, Python version, package versions)
  - Sample data or code if possible

- **Feature Requests**: Have an idea for improvement?
  - Describe the feature and its benefits
  - Provide use cases
  - Suggest implementation approach if you have ideas

### 2. Code Contributions
- **Bug Fixes**: Fix existing issues
- **New Features**: Add new analysis methods
- **Performance Improvements**: Optimize existing code
- **Documentation**: Improve docs and examples
- **Tests**: Add or improve test coverage

### 3. Documentation
- **API Documentation**: Improve function docstrings
- **Examples**: Add new example scripts
- **Tutorials**: Create step-by-step guides
- **FAQ**: Help answer common questions

## 🛠️ Development Setup

### Prerequisites
- Python 3.7 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Steps

1. **Fork and clone the repository:**
```bash
git clone https://github.com/IkjotSidhu/SLEAP-downstream-analysis-pipeline.git
cd sleap-analysis-pipeline
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
pip install pytest pytest-cov  # For testing
```

4. **Install in development mode:**
```bash
pip install -e .
```

5. **Run tests to verify setup:**
```bash
python -m pytest tests/
```

## 📝 Coding Standards

### Style Guidelines
- **PEP 8**: Follow Python style guidelines
- **Line Length**: Maximum 88 characters (Black formatter standard)
- **Imports**: Group imports (standard library, third-party, local)
- **Naming**: Use descriptive variable and function names

### Documentation
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Add type hints for function parameters and returns
- **Comments**: Explain complex logic and algorithms

### Example Function:
```python
def analyze_velocity(locations: np.ndarray, node_index: int, 
                    config: AnalysisConfig) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate velocity profiles for tracked animals.
    
    Args:
        locations: 4D array of tracking data (frames, nodes, coords, instances)
        node_index: Index of the node to analyze
        config: Configuration object with analysis parameters
        
    Returns:
        Tuple of velocity arrays for each instance
        
    Raises:
        ValueError: If node_index is out of bounds
    """
    # Implementation here
    pass
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=sleap_plotting

# Run specific test file
python -m pytest tests/test_pipeline.py
```

### Writing Tests
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test complete workflows
- **Edge Cases**: Test boundary conditions and error cases
- **Test Data**: Use synthetic data for reproducible tests

### Test Structure:
```python
def test_function_name():
    """Test description."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result.shape == expected_shape
    assert np.all(result >= 0)
```

## 🔄 Pull Request Process

### Before Submitting
1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
   - Write clear, focused commits
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
```bash
python -m pytest tests/
```

4. **Update documentation:**
   - Add docstrings for new functions
   - Update README if needed
   - Add examples for new features

### Pull Request Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New functionality includes tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] PR description explains changes

### PR Description Template:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] New tests added
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

## 🎯 Areas for Contribution

### High Priority
- **Performance Optimization**: Improve processing speed for large datasets
- **Memory Efficiency**: Reduce memory usage for long recordings
- **Error Handling**: More robust error handling and user feedback
- **Documentation**: More examples and tutorials

### Medium Priority
- **New Analysis Methods**: 
  - Angular velocity calculations
  - Social behavior metrics
  - Statistical comparisons
  - Behavioral state classification
- **Visualization Improvements**:
  - Interactive plots
  - 3D visualizations
  - Animation capabilities

### Future Enhancements
- **GUI Interface**: User-friendly graphical interface
- **Batch Processing**: Analyze multiple files automatically
- **Data Export**: Export results to various formats
- **Integration**: Connect with other analysis tools

## 🐛 Debugging Tips

### Common Issues
1. **Import Errors**: Check virtual environment and dependencies
2. **File Path Issues**: Use absolute paths or Path objects
3. **Data Shape Errors**: Verify SLEAP data format
4. **Memory Issues**: Process data in chunks for large files

### Debugging Workflow
1. **Reproduce the Issue**: Create minimal example
2. **Check Inputs**: Validate data format and parameters
3. **Add Logging**: Use print statements or logging module
4. **Test Edge Cases**: Check boundary conditions
5. **Review Documentation**: Ensure correct usage

## 📞 Getting Help

### Resources
- **Documentation**: Check README and docstrings
- **Examples**: Look at example scripts
- **Tests**: See test files for usage patterns
- **Issues**: Search existing GitHub issues

### Communication
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas
- **Code Review**: Provide constructive feedback on PRs

## 🏆 Recognition

Contributors will be:
- Added to the contributors list
- Mentioned in release notes
- Credited in documentation
- Invited to be maintainers for significant contributions

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the SLEAP Analysis Pipeline! Your efforts help make animal behavior analysis more accessible and powerful for researchers worldwide. 🎉
