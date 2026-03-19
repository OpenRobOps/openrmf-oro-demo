# Demo ORO Fleet Adapter Package

The objective of this repository is to provide a reference implementation of a fleet adapter that connects a fleet of robots to the OpenRMF ecosystem and the Inorbit fleet management platform. The package `oro_fleet_adapter` contains a generic fleet adapter implementation that can be configured to work with different types of robots and navigation graphs. The package also contains a pre-configured setup for an `Andino` robot operating in a `office` Gazebo simulation environment.

## Step 1: Create env file
Before building the package, it is important to create an `.env` file in the root of the repository and fill in the required parameters. You can use the provided `env_template` file as a template for creating your own `.env` file.

## Step 1.1: Configure the simulation environment (optional)

Check the file `simulation/README.md` for instructions on how to configure the simulation environment.

## Step 2: Build Docker files

Since the package has a lot of dependencies, it is recommended to use the provided Docker files to build the package and run the simulation environment. You can build the docker image using the command below from the root of the repository.

To build the fleet adapter docker image, use the command below from the root of the repository.
```bash
DOCKER_BUILDKIT=1 docker compose build
```

To build the simulation environment docker image, use the command below from the root of the repository.
```bash
./simulation/build.sh
```

## Step 2: Execute the containers

There is a default profile and a `simulation` profile in the `docker-compose.yaml` file, the default profile is used to run the fleet adapter and the simulation profile is used to run the simulation environment. You can execute the containers using the command below.
```bash
docker compose up -d
```
This will start 3 containers:
1. `oro_fleet_adapter` (to run the fleet adapter that connects the robots to RMF and the ORO agent)
2. `open_rmf_api_server` (to run the api server of the RMF backend)
3. `open_rmf_dashboard` (to run the frontend dashboard of RMF)

(optional) If you want to run the simulation environment, you can use the command below to start the simulation container among the fleet and RMF components.
```bash
docker compose --profile robot up -d
```
or just run the command below to start only the robot service container if you want to run the simulation environment in a different machine (useful when you want emulate non local connections).
```bash
docker compose up robot_service
```

And open a web browser and navigate to `http://localhost:3000/robots` to access the RMF web interface and see the robot in action.

<img width="2544" height="900" alt="image" src="https://github.com/user-attachments/assets/658fc6f9-3f70-42e6-b742-c79015159ba4" />
