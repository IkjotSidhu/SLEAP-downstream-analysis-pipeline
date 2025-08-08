"""
Setup script for SLEAP Analysis Pipeline.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="sleap-analysis-pipeline",
    version="1.0.0",
    author="Ikjot Sidhu",
    author_email="ikjotsdh@bu.edu",
    description="A comprehensive Python pipeline for analyzing SLEAP tracking data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IkjotSidhu/SLEAP-downstream-analysis-pipeline",
    py_modules=["sleap_plotting"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "sleap-analyze=sleap_plotting:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/IkjotSidhu/SLEAP-downstream-analysis-pipeline/issues",
        "Source": "https://github.com/IkjotSidhu/SLEAP-downstream-analysis-pipeline",
        "Documentation": "https://github.com/IkjotSidhu/SLEAP-downstream-analysis-pipeline/blob/main/README.md",
    },
    keywords="sleap animal tracking behavior analysis computer vision",
    include_package_data=True,
    zip_safe=False,
)
