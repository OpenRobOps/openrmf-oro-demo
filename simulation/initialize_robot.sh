#!/bin/bash

# Check if a robot name was provided
if [ -z "$1" ]; then
  echo "Usage: ./initialize_robot.sh <robot_name>"
  echo "Example: ./initialize_robot.sh andino1"
  exit 1
fi

export ROBOT_NAME=$1
CONFIG_FILE="robot_config/${ROBOT_NAME}/config.env"

# Verify the configuration folder/file exists
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: Configuration file ${CONFIG_FILE} not found."
  echo "Please ensure the folder 'robot_config/${ROBOT_NAME}' exists and contains a 'config.env' file."
  exit 1
fi

echo "Initializing robot: ${ROBOT_NAME}..."

# We use the -p flag to give each robot its own isolated Compose project name
# Otherwise, Docker Compose will tear down andino1 when you spin up andino2
docker compose -f docker-compose.robot.yml -p "${ROBOT_NAME}_fleet" up -d

echo "${ROBOT_NAME} successfully launched!"