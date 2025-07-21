#!/usr/bin/env bash

# MAAP Build Script for LHASA
# This script sets up the LHASA environment for deployment on NASA's MAAP platform.
# It creates the conda environment, installs MAAP-specific dependencies, and downloads
# required static data files for landslide hazard assessment.

set -xeou pipefail

# Store current working directory and determine script location
workdir=$(pwd)
algodir=$(dirname "$(readlink -f "$0")")
# Use system conda or fallback to conda command
conda=${CONDA_EXE:-conda}

# Change to algorithm directory to access configuration files
cd ${algodir}

# Create LHASA conda environment from specification file
# This installs Python 3.12, XGBoost 2.0, rioxarray, dask, and other dependencies
${conda} env create -y -f lhasa.yml

# Install unzip utility in the lhasa environment for data extraction
${conda} install -n lhasa -y unzip

# Install MAAP Python client for accessing platform services and secrets manager
${conda} run -n lhasa pip install maap-py

# Download and extract required static data files for LHASA operations
# These files contain global datasets needed for landslide prediction

# Static variables: slope, lithology, peak ground acceleration, land mask, precipitation percentiles
wget https://gpm.nasa.gov/sites/default/files/data/landslides/static.zip &&
${conda} run -n lhasa unzip static.zip &&
rm static.zip

# Exposure data: population density, road networks, administrative boundaries
wget https://gpm.nasa.gov/sites/default/files/data/landslides/exposure.zip &&
${conda} run -n lhasa unzip exposure.zip &&
rm exposure.zip

# Reference data for post-fire debris flow (PFDF) model
wget https://gpm.nasa.gov/sites/default/files/data/landslides/ref_data.zip &&
${conda} run -n lhasa unzip ref_data.zip -d pfdf/ &&
rm ref_data.zip
