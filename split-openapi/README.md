# Microsoft Graph API - Split OpenAPI Specification

This directory contains the decomposed OpenAPI specification for the Microsoft Graph API. The original specification, which is publicly available on GitHub, has been split using `redocly split` to organize it into modular files for improved maintainability and readability.

## Directory Structure

- **components/**
  - **schemas/**: Contains individual schema definitions.
  - **responses/**: Contains reusable response objects.
  - **parameters/**: Contains reusable parameters.
  - **examples/**: Contains example payloads.
  - **requestBodies/**: Contains reusable request body objects.
  - **headers/**: Contains reusable header definitions.
  - **securitySchemes/**: Contains security scheme definitions.
  - **links/**: Contains reusable link objects.
  - **callbacks/**: Contains reusable callback objects.
- **paths/**: Contains path definitions, each corresponding to an API endpoint.
- **index.yaml**: The root OpenAPI document that references all components and paths.

## Usage

To work with the split OpenAPI specification, you can use tools like [Redocly CLI](https://redocly.com/docs/cli/).

### Bundling into a Single File

To bundle the split files back into a single OpenAPI document:

```bash
redocly bundle index.yaml --output openapi.yaml
```

This command will generate a consolidated `openapi.yaml` file.

### Previewing Documentation

To preview the API documentation:

```bash
redocly preview-docs index.yaml
```

This will start a local server where you can view the rendered API documentation.

## Contributing

When adding or updating API endpoints:

1. **Paths**: Add new path definitions in the `paths/` directory.
2. **Components**: Add or update schemas, responses, parameters, etc., in the appropriate subdirectory under `components/`.
3. **References**: Ensure that `index.yaml` correctly references the new or updated files.

This modular structure allows for easier collaboration and version control.

## Notes

- Ensure that all YAML files maintain proper syntax and adhere to the OpenAPI Specification.
- Use relative paths for `$ref` references to maintain portability.
- Validate the combined OpenAPI document after making changes to ensure consistency.

For more information on the OpenAPI Specification, visit the [official documentation](https://swagger.io/specification/).
