#!/bin/bash

echo "Starting InstaBreaker 2026 Ultra Edition Setup..."

# Update and upgrade packages
pkg update -y && pkg upgrade -y

# Install Python and necessary build tools
pkg install -y python python-pip clang make pkg-config libffi openssl rust curl

# Install additional libraries that are often problematic in Termux
pkg install -y libxml2 libxslt

# Install python dependencies
pip install --upgrade pip
pip install -e .

# Install curl_cffi separately as it might need build-from-source in some environments
# though usually pip handles it if build tools are present.
pip install curl_cffi

echo "Setup complete! You can now run InstaBreaker with 'instabreaker'"
