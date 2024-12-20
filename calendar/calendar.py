"""
File: calendar.py
Author: Takashi Sasaki
Created: 2024-11-27
Modified: 2024-11-28
Version: 1.4.2

Description:
This script extracts specified paths from a pre-processed OpenAPI document stored as a Pickle file. The extracted
subset is saved in both JSON and YAML formats, ensuring necessary components are included and resolving all $ref dependencies recursively.

Defaults:
    Pickle OpenAPI file: openapi_spec.pkl
    Required paths file: calendar.txt
    Output JSON file: calendar.json
    Output YAML file: calendar.yaml
"""

import os
import sys
import argparse
import yaml
import json
import pickle
import logging

# Configure logging
script_name = os.path.splitext(os.path.basename(__file__))[0]
log_file_name = f"{script_name}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s - %(funcName)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=log_file_name,
    filemode="w",
)
logger = logging.getLogger()


def ensure_correct_directory():
    """Ensure the script is executed from its directory or adjust the current directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.getcwd()

    if script_dir != current_dir:
        logger.info(f"Adjusting current directory to: {script_dir}")
        os.chdir(script_dir)


def load_pickle_file(file_path):
    """Load a pickle file, and handle potential errors."""
    logger.info(f"Attempting to load Pickle file: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"Error: The file {file_path} does not exist.")
        return None

    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        logger.info(f"Successfully loaded pickle file: {file_path}")
        return data
    except pickle.UnpicklingError:
        logger.error(f"Error: Failed to unpickle the file {file_path}. The file may be corrupted or incompatible.")
        return None
    except Exception as e:
        logger.error(f"Error: {e}")
        return None


def load_required_paths(file_path):
    """Load the required paths from a text file."""
    logger.info(f"Loading required paths from: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        logger.error(f"Failed to load required paths from {file_path}: {e}")
        raise


def collect_refs(data, used_refs, current_path="root"):
    """Recursively collect all $ref values from the OpenAPI document."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "$ref" and isinstance(value, str):
                if value not in used_refs:
                    used_refs.add(value)
                    # Log the reference found and the current size of used_refs
                    logger.debug(f"Found reference at {current_path}: {value}")
                    logger.debug(f"Current size of used_refs: {len(used_refs)}")  # Log size of used_refs after addition
            else:
                collect_refs(value, used_refs, f"{current_path}/{key}")
    elif isinstance(data, list):
        for index, item in enumerate(data):
            collect_refs(item, used_refs, f"{current_path}[{index}]")



def resolve_refs_recursive(openapi_spec, used_refs):
    """Resolve all $ref dependencies recursively and include necessary components."""
    logger.info(f"Resolving $refs recursively.")
    components = openapi_spec.get("components", {})
    resolved_components = {key: {} for key in components}

    # Debug log: Total number of components available
    total_components = sum(len(items) for items in components.values())
    logger.debug(f"Total components available: {total_components}")

    def resolve_component(ref):
        if ref.startswith("#/components/"):
            try:
                _, _, comp_type, name = ref.split("/", 3)
                if comp_type not in components:
                    logger.warning(f"Component type '{comp_type}' not found for $ref: {ref}")
                    return
                if name not in components[comp_type]:
                    logger.warning(f"Component '{name}' not found in type '{comp_type}' for $ref: {ref}")
                    return
                if name not in resolved_components[comp_type]:
                    # Add the component
                    resolved_components[comp_type][name] = components[comp_type][name]
                    logger.debug(f"Resolved component: {comp_type}/{name}")
                    # Recursively resolve nested $refs
                    collect_refs(components[comp_type][name], used_refs, f"#/components/{comp_type}/{name}")
            except ValueError as e:
                logger.error(f"Malformed $ref: {ref} ({e})")
        else:
            logger.warning(f"$ref '{ref}' does not start with '#/components/', skipping.")


    # Resolve all collected refs
    for ref in list(used_refs):
        logger.debug(f"Processing $ref: {ref}")
        resolve_component(ref)

    # Debug log: resolved components
    resolved_count = sum(len(items) for items in resolved_components.values())
    logger.debug(f"Resolved components count: {resolved_count}")

    # Return resolved components
    return {k: v for k, v in resolved_components.items() if v}


def filter_openapi_spec(openapi_spec, required_paths):
    """Filter the OpenAPI spec to include only the required paths and resolve $refs."""
    logger.info(f"Filtering OpenAPI spec to include only the required paths.")
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

    # Collect all used $refs
    used_refs = set()
    collect_refs(filtered_paths, used_refs)

    # Debug log: Number of $refs collected
    logger.debug(f"Number of $refs collected: {len(used_refs)}")

    # Resolve $ref dependencies recursively
    resolved_components = resolve_refs_recursive(openapi_spec, used_refs)

    # Include resolved components in the spec
    if resolved_components:
        openapi_spec['components'] = resolved_components
    else:
        openapi_spec.pop('components', None)

    return openapi_spec


def save_file(data, file_path):
    """Save OpenAPI data to a file in YAML or JSON format."""
    logger.info(f"Saving filtered OpenAPI spec to: {file_path}")
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                yaml.safe_dump(data, file, allow_unicode=True)
            elif file_path.endswith('.json'):
                json.dump(data, file, indent=2)
            else:
                raise ValueError("Unsupported output format. Please use a .yaml or .json extension.")
        logger.info(f"Saved file '{file_path}'.")
    except Exception as e:
        logger.error(f"Failed to save file {file_path}: {e}")
        raise


def main():
    # Ensure the script is run from its directory
    ensure_correct_directory()

    parser = argparse.ArgumentParser(description="Extract specified paths from an OpenAPI document.")
    parser.add_argument("--output_json", help="Path to the output JSON file.", default="calendar.json")
    parser.add_argument("--output_yaml", help="Path to the output YAML file.", default="calendar.yaml")
    parser.add_argument("--required_paths_file", help="Path to the text file containing required paths.", default="calendar.txt")

    args = parser.parse_args()

    # Check for pickle file
    pkl_file_path = "openapi_spec.pkl"
    openapi_spec = load_pickle_file(pkl_file_path)

    # If pickle file doesn't exist or loading failed, stop execution
    if not openapi_spec:
        logger.error("Pickle file loading failed. Exiting.")
        sys.exit(1)

    # Load required paths
    required_paths = load_required_paths(args.required_paths_file)

    # Filter OpenAPI spec
    filtered_spec = filter_openapi_spec(openapi_spec, required_paths)

    # Save output OpenAPI file(s)
    save_file(filtered_spec, args.output_json)
    logger.info(f"Filtered OpenAPI spec saved to {args.output_json}")
    save_file(filtered_spec, args.output_yaml)
    logger.info(f"Filtered OpenAPI spec saved to {args.output_yaml}")


if __name__ == "__main__":
    main()
