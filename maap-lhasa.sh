#!/usr/bin/env bash

# MAAP Execution Script for LHASA
# This script runs the LHASA landslide forecasting system on NASA's MAAP platform.
# It sets up the required output directory structure, configures authentication
# using MAAP secrets manager, and executes the main LHASA prediction workflow.

set -xeou pipefail

# Store current working directory and determine script location
workdir=$(pwd)
algodir=$(dirname "$(readlink -f "$0")")
# Use system conda or fallback to conda command
conda=${CONDA_EXE:-conda}

# Create LHASA output directory structure in the working directory
# This separates near real-time (nrt) and forecast (fcast) products
# Each category has subdirectories for hazard maps and exposure analysis

# Near real-time landslide hazard outputs
mkdir -p ${workdir}/output/nrt/hazard/tif
mkdir -p ${workdir}/output/nrt/exposure/csv

# Forecast landslide hazard outputs (1-2 days ahead)
mkdir -p ${workdir}/output/fcast/hazard/tif
mkdir -p ${workdir}/output/fcast/exposure/csv

# Cache directory for IMERG precipitation data downloads
mkdir -p ${workdir}/output/imerg

# Change to algorithm directory to access LHASA code and configuration
cd ${algodir}

# Configure authentication using MAAP secrets manager
# This automatically retrieves NASA Earthdata and PPS credentials from MAAP
# and writes them to ~/.netrc for automated data access
${conda} run -n lhasa python configure_netrc.py

# Execute LHASA with MAAP-specific configuration
# -t 4: Use 4 threads for XGBoost model inference
# --output_path: Direct outputs to working directory instead of algorithm directory
${conda} run -n lhasa python lhasa.py -t 8 -ex -f nc4tif -output_path ${workdir}/output
