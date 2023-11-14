# SITL-LAUNCHER

This is a simple Python project with an installer.

## Build Instructions

1. **Build your Python package:**

    pip install setuptools wheel click

    python setup.py sdist bdist_wheel

2. **Distribute your package, for example, by uploading to PyPI:**
    
    pip install twine
    twine upload dist/*

## Installation

To install the project and run the installer, follow these steps:

1. **Install the project using pip:**

   ```bash
   pip install my_project