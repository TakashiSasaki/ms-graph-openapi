"""
File: calendar.py
Author: Takashi Sasaki
Created: 2024-11-27
Version: 1.0.1

Description:
This script extracts specified paths from an OpenAPI document. The extracted
subset is saved in both JSON and YAML formats, excluding the `tags` property.

Defaults:
    Input OpenAPI file: ../github/openapi/v1.0/openapi.yaml
    Required paths file: calendar.txt
    Output JSON file: calendar.json
    Output YAML file: calendar.yaml
"""
import argparse
import yaml
import json

def load_file(file_path):
    """Load a YAML or JSON OpenAPI file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            return yaml.safe_load(file)
        elif file_path.endswith('.json'):
            return json.load(file)
        else:
            raise ValueError("Unsupported file format. Please use a YAML or JSON file.")

def save_file(data, file_path):
    """Save OpenAPI data to a file in YAML or JSON format."""
    with open(file_path, 'w', encoding='utf-8') as file:
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            yaml.safe_dump(data, file, allow_unicode=True)
        elif file_path.endswith('.json'):
            json.dump(data, file, indent=2)
        else:
            raise ValueError("Unsupported output format. Please use a .yaml or .json extension.")

def load_required_paths(file_path):
    """Load the required paths from a text file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

def filter_openapi_spec(openapi_spec, required_paths):
    """Filter the OpenAPI spec to include only the required paths and exclude tags."""
    # Filter paths
    filtered_paths = {path: openapi_spec['paths'][path] for path in openapi_spec['paths'] if path in required_paths}

    # Remove `tags` property from the filtered paths
    for path, methods in filtered_paths.items():
        for method, details in methods.items():
            if isinstance(details, dict) and "tags" in details:
                del details["tags"]

    openapi_spec['paths'] = filtered_paths

    # Remove `tags` property from the root-level specification
    if "tags" in openapi_spec:
        del openapi_spec["tags"]

    return openapi_spec

def main():
    parser = argparse.ArgumentParser(description="Extract specified paths from an OpenAPI document.")
    parser.add_argument("--input_file", help="Path to the input OpenAPI YAML or JSON file.", default="../github/openapi/v1.0/openapi.yaml")
    parser.add_argument("--output_json", help="Path to the output JSON file.", default="calendar.json")
    parser.add_argument("--output_yaml", help="Path to the output YAML file.", default="calendar.yaml")
    parser.add_argument("--required_paths_file", help="Path to the text file containing required paths.", default="calendar.txt")
    
    args = parser.parse_args()

    # Load input OpenAPI file
    openapi_spec = load_file(args.input_file)
    
    # Load required paths
    required_paths = load_required_paths(args.required_paths_file)
    
    # Filter OpenAPI spec
    filtered_spec = filter_openapi_spec(openapi_spec, required_paths)
    
    # Save output OpenAPI file(s)
    save_file(filtered_spec, args.output_json)
    print(f"Filtered OpenAPI spec saved to {args.output_json}")
    save_file(filtered_spec, args.output_yaml)
    print(f"Filtered OpenAPI spec saved to {args.output_yaml}")

if __name__ == "__main__":
    main()
