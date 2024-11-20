#!/bin/bash

# Run Docker Compose to start the services in detached mode and build the images if necessary
cd infrastructure
docker-compose up -d --build