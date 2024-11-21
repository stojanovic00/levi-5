#!/bin/bash

RED='\033[0;31m'
NC='\033[0m' # No Color

cd infrastructure
docker-compose down
echo -e "${RED}Matchmaking API stopped${NC}"
