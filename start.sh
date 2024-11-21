#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Run Docker Compose to start the services in detached mode and build the images if necessary
cd infrastructure
docker-compose up -d --build
echo -e "${GREEN}Matchmaking API started and listening on localhost:8080${NC}"
