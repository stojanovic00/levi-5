# Matchmaking API

## Overview

This is a Matchmaking API built with Flask and Redis. The application allows you to manage players, teams, and matches.

## Dependencies

To build and run this application, you need the following dependencies:

- **Docker**: Docker is required to build and run the Docker containers.
  - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: Docker Compose is required to manage multi-container Docker applications.
  - [Install Docker Compose](https://docs.docker.com/compose/install/)

## Build and run

- Building and running application is done by running `./start.sh`
- Stopping the application is done by running `./stop.sh`

## Technologies Used

- **Flask**: A lightweight WSGI web application framework in Python. It is designed with simplicity and flexibility in mind, making it easy to build web applications quickly.
- **Redis**: An in-memory data structure store used as a database, cache, and message broker. It supports various data structures such as strings, hashes, lists, sets, and more. Redis is known for its high performance and scalability.

- **Docker**: A platform for developing, shipping, and running applications inside containers. It allows you to package an application with all its dependencies into a standardized unit for software development. Docker ensures that your application runs consistently across different environments.

- **Docker Compose**: A tool for defining and running multi-container Docker applications. It uses a YAML file to configure the application's services, networks, and volumes. Docker Compose makes it easy to manage and orchestrate multiple containers as a single service.
