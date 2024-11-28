"""
File: calendar.py
Author: Takashi Sasaki
Created: 2024-11-27
Modified: 2024-11-28
Version: 1.1.5

Description:
This script extracts specified paths from an OpenAPI document. The extracted
subset is saved in both JSON and YAML formats, ensuring necessary components
are included and resolving all $ref dependencies recursively.

Defaults:
    Input OpenAPI file: ../github/openapi/v1.0/openapi.yaml
    Required paths file: calendar.txt
    Output JSON file: calendar.json
    Output YAML file: calendar.yaml
"""
import os
import sys
import argparse
import yaml
import json
import time


def ensure_correct_directory():
    """Ensure the script is executed from its directory or adjust the current directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.getcwd()

    if script_dir != current_dir:
        print(f"Adjusting current directory to: {script_dir}")
        os.chdir(script_dir)


def load_file(file_path):
    """Load a YAML or JSON OpenAPI file."""
    start_time = time.time()
    with open(file_path, 'r', encoding='utf-8') as file:
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            result = yaml.safe_load(file)
        elif file_path.endswith('.json'):
            result = json.load(file)
        else:
            raise ValueError("Unsupported file format. Please use a YAML or JSON file.")
    elapsed_time = time.time() - start_time
    print(f"Loaded file '{file_path}' in {elapsed_time:.2f} seconds.", file=sys.stderr)
    return result


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
        paths = [line.strip() for line in file if line.strip()]
    print("Loaded required paths:", file=sys.stderr)
    for i, path in enumerate(paths, start=1):
        print(f"{i}: {path}", file=sys.stderr)
    return paths


def collect_refs(data, used_refs, current_path="root"):
    """Recursively collect all $ref values from the OpenAPI document."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "$ref" and isinstance(value, str):
                if value not in used_refs:
                    used_refs.add(value)
                    print(f"Found reference at {current_path}: {value}", file=sys.stderr)
            else:
                collect_refs(value, used_refs, f"{current_path}/{key}")
    elif isinstance(data, list):
        for index, item in enumerate(data):
            collect_refs(item, used_refs, f"{current_path}[{index}]")


def resolve_refs_recursive(openapi_spec, used_refs):
    """Resolve all $ref dependencies recursively and include necessary components."""
    components = openapi_spec.get("components", {})
    resolved_components = {key: {} for key in components}

    total_components = sum(len(items) for items in components.values())
    print(f"Total components available: {total_components}", file=sys.stderr)

    def resolve_component(ref):
        if ref.startswith("#/components/"):
            try:
                parts = ref.split("/")
                if len(parts) < 4:
                    print(f"Malformed $ref: {ref}", file=sys.stderr)
                    return
                _, _, comp_type, name = parts
                if comp_type not in components:
                    print(f"Component type '{comp_type}' not found for $ref: {ref}", file=sys.stderr)
                    return
                if name not in components[comp_type]:
                    print(f"Component '{name}' not found in type '{comp_type}' for $ref: {ref}", file=sys.stderr)
                    return
                if name not in resolved_components[comp_type]:
                    resolved_components[comp_type][name] = components[comp_type][name]
                    print(f"Resolved component: {comp_type}/{name}", file=sys.stderr)
                    collect_refs(components[comp_type][name], used_refs, f"#/components/{comp_type}/{name}")
            except ValueError as e:
                print(f"Error processing $ref '{ref}': {e}", file=sys.stderr)

    for ref in list(used_refs):
        print(f"Processing $ref: {ref}", file=sys.stderr)
        resolve_component(ref)

    resolved_count = sum(len(items) for items in resolved_components.values())
    print(f"Resolved components count: {resolved_count}", file=sys.stderr)

    return {k: v for k, v in resolved_components.items() if v}


def filter_openapi_spec(openapi_spec, required_paths):
    """Filter the OpenAPI spec to include only the required paths and resolve $refs."""
    print("Filtering OpenAPI specification...", file=sys.stderr)
    start_time = time.time()
    filtered_paths = {path: openapi_spec['paths'][path] for path in openapi_spec['paths'] if path in required_paths}

    for path, methods in filtered_paths.items():
        for method, details in methods.items():
            if isinstance(details, dict) and "tags" in details:
                del details["tags"]

    openapi_spec['paths'] = filtered_paths

    if "tags" in openapi_spec:
        del openapi_spec["tags"]

    used_refs = set()
    collect_refs(filtered_paths, used_refs)

    print(f"Number of $refs collected: {len(used_refs)}", file=sys.stderr)
    resolved_components = resolve_refs_recursive(openapi_spec, used_refs)

    if resolved_components:
        openapi_spec['components'] = resolved_components
    else:
        openapi_spec.pop('components', None)

    elapsed_time = time.time() - start_time
    print(f"Filtering completed in {elapsed_time:.2f} seconds.", file=sys.stderr)

    return openapi_spec


def main():
    ensure_correct_directory()

    parser = argparse.ArgumentParser(description="Extract specified paths from an OpenAPI document.")
    parser.add_argument("--input_file", help="Path to the input OpenAPI YAML or JSON file.", default="../github/openapi/v1.0/openapi.yaml")
    parser.add_argument("--output_json", help="Path to the output JSON file.", default="calendar.json")
    parser.add_argument("--output_yaml", help="Path to the output YAML file.", default="calendar.yaml")
    parser.add_argument("--required_paths_file", help="Path to the text file containing required paths.", default="calendar.txt")

    args = parser.parse_args()

    openapi_spec = load_file(args.input_file)
    required_paths = load_required_paths(args.required_paths_file)

    print("Starting to filter the OpenAPI specification...", file=sys.stderr)
    filtered_spec = filter_openapi_spec(openapi_spec, required_paths)
    print("Finished filtering the OpenAPI specification.", file=sys.stderr)

    save_file(filtered_spec, args.output_json)
    print(f"Filtered OpenAPI spec saved to {args.output_json}")
    save_file(filtered_spec, args.output_yaml)
    print(f"Filtered OpenAPI spec saved to {args.output_yaml}")


if __name__ == "__main__":
    main()
