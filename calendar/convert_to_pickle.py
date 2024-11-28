"""
File: convert_to_pickle.py
Author: Takashi Sasaki
Created: 2024-11-29
Version: 1.0.0

Description:
This script converts the provided OpenAPI document (YAML or JSON) into a Pickle file for faster future loading.
The script will set its directory as the current working directory.

Defaults:
    Input OpenAPI file: ../github/openapi/v1.0/openapi.yaml
    Output Pickle file: openapi_spec.pkl
"""

import os
import sys
import argparse
import yaml
import json
import pickle
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

def ensure_correct_directory():
    """Ensure the script is executed from its directory or adjust the current directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.getcwd()

    if script_dir != current_dir:
        logger.info(f"Adjusting current directory to: {script_dir}")
        os.chdir(script_dir)

def load_file(file_path):
    """Load a YAML or JSON OpenAPI file."""
    logger.info(f"Loading file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            return yaml.safe_load(file)
        elif file_path.endswith('.json'):
            return json.load(file)
        else:
            raise ValueError("Unsupported file format. Please use a YAML or JSON file.")

def save_pickle(data, file_path):
    """Save data to a Pickle file."""
    logger.info(f"Saving Pickle file: {file_path}")
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)
    logger.info(f"Pickle file saved to {file_path}")

def load_pickle(file_path):
    """Load data from a Pickle file."""
    if os.path.exists(file_path):
        logger.info(f"Attempting to load Pickle file: {file_path}")
        try:
            with open(file_path, 'rb') as file:
                return pickle.load(file)
        except (pickle.UnpicklingError, EOFError, ValueError) as e:
            logger.error(f"Failed to load Pickle file: {file_path}. Error: {e}")
    return None

def convert_to_pickle(input_file, pickle_file):
    """Convert OpenAPI file to Pickle format."""
    # Try to load Pickle first
    openapi_spec = load_pickle(pickle_file)
    
    if openapi_spec is None:
        # Load the OpenAPI document from YAML or JSON if Pickle is not available
        openapi_spec = load_file(input_file)
        # Save the loaded OpenAPI spec to a Pickle file
        save_pickle(openapi_spec, pickle_file)
    
    return openapi_spec

def main():
    """Main function to handle input arguments and execute the conversion."""
    # Ensure the script is run from its directory
    ensure_correct_directory()

    parser = argparse.ArgumentParser(description="Convert OpenAPI YAML/JSON to Pickle format for faster future loading.")
    parser.add_argument("--input_file", help="Path to the input OpenAPI YAML or JSON file.", default="../github/openapi/v1.0/openapi.yaml")
    parser.add_argument("--output_pickle", help="Path to the output Pickle file.", default="openapi_spec.pkl")

    args = parser.parse_args()

    # Convert OpenAPI document to Pickle
    openapi_spec = convert_to_pickle(args.input_file, args.output_pickle)

    # Optionally, you can log the structure or part of the OpenAPI spec
    logger.debug(f"OpenAPI document structure: {openapi_spec.keys()}")

if __name__ == "__main__":
    main()
