"""
Script Name: list_openapi_endpoints.py
Author: Takashi Sasaki
Created Date: 2024-11-26
Version: 1.4

Description:
This script extracts and outputs a list of endpoints (paths) and their corresponding HTTP methods
from an OpenAPI document provided in YAML format. It uses a graphical progress bar for user feedback
and saves the output to a file. Default input and output file paths are predefined.
"""

import yaml
from tqdm import tqdm

def list_endpoints_with_progress(openapi_file, output_file):
    """
    Extracts and outputs all endpoints and their HTTP methods from the OpenAPI document with a graphical progress bar.

    Args:
        openapi_file (str): Path to the OpenAPI YAML file.
        output_file (str): Path to the output file where results will be saved.

    Returns:
        None
    """
    try:
        # Display message before loading YAML
        print(f"Loading OpenAPI document from '{openapi_file}'...")
        
        # Load the OpenAPI document
        with open(openapi_file, 'r', encoding='utf-8') as f:
            openapi = yaml.safe_load(f)
        
        # Display message after loading YAML
        print(f"OpenAPI document loaded successfully.")

        # Check if `paths` is present in the document
        if 'paths' not in openapi:
            print("No `paths` section found in the OpenAPI document.")
            return

        # Get total number of paths for progress tracking
        total_paths = len(openapi['paths'])
        if total_paths == 0:
            print("No paths found in the OpenAPI document.")
            return

        # Open the output file for writing
        with open(output_file, 'w', encoding='utf-8') as out_file:
            out_file.write("Endpoints found in the OpenAPI document:\n")

            # Iterate through paths and methods with progress bar
            for path, methods in tqdm(openapi['paths'].items(), total=total_paths, desc="Processing Endpoints"):
                out_file.write(f"Path: {path}\n")
                for method in methods.keys():
                    out_file.write(f"  - Method: {method.upper()}\n")
                out_file.write("\n")  # Blank line for readability

        print(f"Output written to {output_file}")

    except FileNotFoundError:
        print(f"Error: File '{openapi_file}' not found.")
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML file. Details: {e}")

if __name__ == "__main__":
    # Default input and output file paths
    openapi_file = "github/openapi/v1.0/openapi.yaml"  # Default input file
    output_file = "openapi-endpoints.txt"             # Default output file

    list_endpoints_with_progress(openapi_file, output_file)
