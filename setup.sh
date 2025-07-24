#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install R dependencies
Rscript install_r_packages.R

# Verify installations
python -c "from plantcv import plantcv; print('PlantCV installed')"
Rscript -e "library(ggplot2); print('ggplot2 installed')"
