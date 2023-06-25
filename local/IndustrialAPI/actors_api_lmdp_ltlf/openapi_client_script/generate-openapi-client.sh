#!/usr/bin/env bash

# This script uses the 'openapi-python-client' tool to generate a Python HTTP client from OpenAPI specification.

# remove previous output if any
/bin/rm -rf industrial-api-client
/bin/rm -rf ../client

# generate new client
/home/aida/.local/bin/openapi-python-client generate --path ../spec.yml

# move generate Python package as a subpackage of ours
mv industrial-api-client/industrial_api_client ../client

# remove temporary output
/bin/rm -rf industrial-api-client
