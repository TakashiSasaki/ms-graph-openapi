"""
Script Name: filter_openapi_paths.py
Author: Takashi Sasaki
Created Date: 2024-11-26
Version: 1.0

Description:
This script extracts and filters OpenAPI endpoint paths based on a given substring.
The input OpenAPI document is in YAML format, and the matching paths are output
as plain text to the standard output. The substring to search for is provided
as a command-line argument.
"""

import yaml
import argparse
import sys

def filter_paths(openapi_file, substring):
    """
    Filters endpoint paths in the OpenAPI document that contain the specified substring.

    Args:
        openapi_file (str): Path to the OpenAPI YAML file.
        substring (str): Substring to search for in the endpoint paths.

    Returns:
        None
    """
    try:
        # Load the OpenAPI document
        with open(openapi_file, 'r', encoding='utf-8') as f:
            openapi = yaml.safe_load(f)

        # Check if `paths` is present in the document
        if 'paths' not in openapi:
            print("No `paths` section found in the OpenAPI document.", file=sys.stderr)
            return

        # Filter paths containing the substring
        matching_paths = [path for path in openapi['paths'] if substring in path]

        # Output the matching paths
        for path in matching_paths:
            print(path)

    except FileNotFoundError:
        print(f"Error: File '{openapi_file}' not found.", file=sys.stderr)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML file. Details: {e}", file=sys.stderr)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Filter OpenAPI endpoint paths based on a given substring."
    )
    parser.add_argument(
        "substring",
        help="The substring to search for in the endpoint paths."
    )
    parser.add_argument(
        "--input",
        default="github/openapi/v1.0/openapi.yaml",
        help="Path to the OpenAPI YAML file (default: github/openapi/v1.0/openapi.yaml)."
    )
    args = parser.parse_args()

    # Call the filter function
    filter_paths(args.input, args.substring)
