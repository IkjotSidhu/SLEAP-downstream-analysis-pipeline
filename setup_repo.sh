#!/bin/bash

# SLEAP Analysis Pipeline - Repository Setup Script
# This script initializes a git repository and sets up the project structure

echo "🚀 Setting up SLEAP Analysis Pipeline repository..."
echo "📁 Working directory: $(pwd)"

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add all files to git
echo "📝 Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: SLEAP Analysis Pipeline v1.0.0

- Complete analysis pipeline for SLEAP tracking data
- Modular functions for trajectory, distance, and velocity analysis
- Configuration system with AnalysisConfig class
- Robust error handling and data validation
- Publication-quality visualizations
- Comprehensive documentation and examples
- Unit test suite with pytest
- CI/CD pipeline with GitHub Actions"

echo "🎉 Repository setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub named 'sleap-analysis-pipeline'"
echo "2. Add the remote origin:"
echo "   git remote add origin https://github.com/yourusername/sleap-analysis-pipeline.git"
echo "3. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "🔧 To install the package locally for development:"
echo "   pip install -e ."
echo ""
echo "🧪 To run tests:"
echo "   python -m pytest tests/"
echo ""
echo "📖 To view documentation:"
echo "   Open README.md in your browser or text editor"
echo ""
echo "🗂️  Project structure:"
echo "   sleap-analysis-pipeline/"
echo "   ├── sleap_plotting.py      # Main pipeline"
echo "   ├── requirements.txt       # Dependencies"
echo "   ├── setup.py              # Package setup"
echo "   ├── examples/             # Usage examples"
echo "   ├── tests/                # Test suite"
echo "   └── .github/              # GitHub workflows"
echo ""
echo "Happy analyzing! 🎯"
