# OpenRMF–ORO Demo

This repository contains a complete demonstration of integrating an Open-RMF deployment with the ORO (InOrbit-compatible) fleet management platform using an Andino robot fleet. It includes:

- A configurable fleet adapter that bridges RMF tasks with ORO robots.
- An RMF backend (API server + trajectory server) and RMF dashboard.
- A Docker-based Andino simulation that connects to both RMF and ORO.

The goal is to provide an end-to-end example: ORO UI → RMF tasks → simulated Andino robots.

For more details about the fleet adapter package itself, see the openrmf-oro-adapter repository README:

- https://github.com/OpenRobOps/openrmf-oro-adapter/blob/main/README.md

That document explains the generic `oro_fleet_adapter` and how it can be configured for different robots and navigation graphs.

## 1. Configuration

### 1.1 Simulation configuration (optional)

If you want to run the Andino Gazebo simulation and connect robots to ORO, follow:

- [simulation/README.md](simulation/README.md)

That README covers:

- Building the Andino simulation image.
- Creating per-robot `config.env` files (e.g., `andino1`, `andino2`).
- Setting up shared ORO / InOrbit configuration in `common.env`.
- Initializing and localizing robots in Gazebo / RViz.

### 1.2 RMF dashboard configuration

The RMF dashboard build and runtime configuration (including how `RMF_SERVER_URL` and `TRAJECTORY_SERVER_URL` are injected) is documented in:

- [rmf_dashboard/README.md](rmf_dashboard/README.md)

You normally do not need to change this for the default demo, but it is useful if you move the RMF services to different hosts.

### 1.4 Fleet adapter configuration and robots

The fleet adapter used here comes from the openrmf-oro-adapter project. The primary documentation is:

- https://github.com/OpenRobOps/openrmf-oro-adapter/blob/main/README.md

For the Andino demo configuration, see:

- https://github.com/OpenRobOps/openrmf-oro-adapter/blob/main/oro_fleet_adapter/demo.andino.config.yaml

In this demo, the fleet adapter is preconfigured to work with two robots: **andino1** and **andino2**. The information in `demo.andino.config.yaml` (or a custom configuration file you create) must be consistent with the robots you bring up in the simulation:

- Robot names and RMF fleet names.
- Navigation graphs and task parameters.
- Any ORO / InOrbit identifiers referenced by the adapter.

If you want to add more robots (e.g., `andino3`, `andino4`):

1. Extend the adapter configuration file (either `demo.andino.config.yaml` or your own) to include the additional robots.
2. Mount that configuration file into the fleet adapter container and update the entrypoint or launch command so the adapter uses your file instead of the default one.
3. Create matching `robot_config/<robot_name>/config.env` files in the `simulation/` directory (see [simulation/README.md](simulation/README.md)).

## 2. Building the Docker images

From the root of this repository:

1. Build the fleet adapter, RMF API server integration, and RMF dashboard images:

```bash
DOCKER_BUILDKIT=1 docker compose build
```

This will build:
- `oro_fleet_adapter` – Fleet adapter container.
- `open_rmf_dashboard` – RMF dashboard served via NGINX.

2. (Optional but recommended) Build the Andino simulation image:

```bash
./simulation/build.sh
```

Details of the simulation build are in [simulation/README.md](simulation/README.md).

## 3. Running the full ORO + RMF stack

Running the full demo involves two pieces:

1. The **ORO platform** (web app, MQTT, ingest, etc.).
2. The **RMF + fleet adapter stack** from this repository.
3. The **Andino simulation** with one or more robots if the default fleet adapter is used.

### 3.1 Start the ORO platform

See https://github.com/OpenRobOps/oro/blob/main/README-dev.md for detailed instructions on how to start the ORO services. If you have the ORO repository cloned in the same workspace (typically as `oro/`), you can also use the VS Code task `🚀 Start All ORO Services` to bring up the ORO stack, which starts:

- MQTT broker.
- ORO web app.
- ORO ingest service.

Ensure the ORO web UI is reachable on port **3000** before proceeding.

### 3.2 Start the RMF + fleet adapter stack

From this repository root, start the fleet profile:

```bash
docker compose up -d
```

This launches:

1. `oro_fleet_adapter` – Connects RMF tasks with ORO robots.
2. `open_rmf_api_server` – RMF API and trajectory server backend.
3. `open_rmf_dashboard` – RMF dashboard web UI.
4. `robots-mock-api` – Mock ORO API server (currently used as a stand-in for some InOrbit endpoints).

You should now be able to:

- Open the ORO UI at `http://localhost:3000/`.
- Open the RMF dashboard at `http://localhost:3011/`.

## 4. Starting robots with the simulation

With ORO and the fleet profile running, you can start simulated robots from the `simulation/` directory.

For example, to start **andino1** and **andino2**:

```bash
cd simulation
./initialize_robot.sh andino1
./initialize_robot.sh andino2
```

Each script call:

- Uses `docker-compose.robot.yml` to bring up a per-robot container.
- Reads `robot_config/<robot_name>/config.env` and `common.env`.
- Installs and runs the InOrbit agent and starts Gazebo + RViz for that robot.

Make sure the environment variables (`INORBIT_ID`... etc) align with what is configured in the fleet adapter’s `demo.andino.config.yaml` (or your custom config) so that RMF and ORO recognize the robots correctly.

For information about localization in RViz and multi-robot setups, see [simulation/README.md](simulation/README.md).

## 5. Ports used

The full demo uses the following ports:

- **3000** – ORO dashboard (web UI).
- **3001** – ORO MQTT broker.
- **3010** – ORO API mock (Mockoon-based service used as an InOrbit-like API) (only launched with the `mock` profile and used as a testing method).
- **3011** – RMF dashboard (`open_rmf_dashboard` service).
- **8000** – RMF API server (`open_rmf_api_server`, used as `RMF_SERVER_URL`).
- **8006** – RMF trajectory server (WebSocket, used as `TRAJECTORY_SERVER_URL`).

Depending on your ORO deployment, additional ports may also be in use; refer to the ORO repository documentation for those details.

## 6. ROS domain IDs

ROS 2 domains are used to separate communication between the different components:

- **0** – Fleet adapter, RMF API server, RMF dashboard.
- **10** – `andino1` simulated robot.
- **11** – `andino2` simulated robot.

Make sure the `ROS_DOMAIN_ID` values in your robot `config.env` files match these defaults or adjust them consistently across the fleet adapter config and the simulation.
