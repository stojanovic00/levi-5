#!/bin/bash

# Set the PYTHONPATH environment variable to include the ./app directory
# This ensures that Python can find and import modules from the app directory

# Run the unittest module as a script with the discover subcommand
# -m runs the unittest module as a script
# -s specifies the start directory for test discovery, which is app/test in this case
# -v increases the verbosity of the test output, showing detailed information about each test
PYTHONPATH=./app python -m unittest discover -v -s app/test