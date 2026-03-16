# oro_fleet_adapter

The objective of this package is to serve as a reference or template for writing a python based `full_control` RMF fleet adapter.

> Note: The implementation in this package is not the only way to write a `full_control` fleet adapter. It is only one such example that may be helpful for users to quickly integrate their fleets with RMF.

## Step 1: Update config.yaml
The `config.yaml` file contains important parameters for setting up the fleet adapter. There are three broad sections to this file:

1. **rmf_fleet** : containing parameters that describe the robots in this fleet
2. **robots** : containing configurations for each robot that will be controlled by this fleet adapter
3. **reference_coordinates**: containing two sets of [x,y] coordinates that correspond to the same locations but recorded in RMF (`traffic_editor`) and robot specific coordinates frames respectively. These are required to estimate coordinate transformations from one frame to another. A minimum of 4 matching waypoints is recommended.

> Note: This fleet adapter uses the `nudged` python library to compute transformations from RMF to Robot frame and vice versa. If the user is aware of the `scale`, `rotation` and `translation` values for each transform, they may modify the code in `fleet_adapter.py` to directly create the `nudged` transform objects from these values.

## Step 2: Build the package
Use the command below to build the package after filling in the code and updating the configuration file.
```bash
colcon build
source install/setup.bash
```

## Step 3: Run the simulation environment
If you do not have access to a physical fleet of robots, you can use the `andino_fleet` package which provides a Gazebo simulation environment with an `Andino` robot. You can launch the simulation environment using the command below. This will spawn 1 `Andino` robot in the `populated office` Gazebo world, the package `oro_fleet_adapter` has a pre-configured fleet adapter configuration file to work with this setup.

```bash
ros2 launch oro_fleet_adapter fleet.andino.sim.launch.xml
```

## Step 3.1: Install the Inorbit agent
Since the Inorbit is going to act as the fleet manager of an andino robot, it is important to have the agent up and running. You can install the agent using the command below. Once installed, you can start the agent using the command shown below.

```bash
curl -fsSL https://control.inorbit.ai/liftoff/mwZZ50wpoCOh33bM -o /tmp/installer.sh
sed -i '/Press ENTER to resume installation or CTRL\+C to cancel\./d;/read -r input <\/dev\/tty/d' /tmp/installer.sh
sh /tmp/installer.sh
```

**Execute the command below to start the agent, (the agent has to be running after the simulation environment is launched leave this command running on a separate terminal, if the simulation is finished the agent will need to be restarted again so it can refresh the `/tf` topic subscriptions and avoid stale data issues):**
```bash
$HOME/.inorbit/dist/scripts/start.sh
```

## Step 5: Run the fleet adapter:

Run the command below while passing the paths to the configuration file and navigation graph that this fleet operates on.

The websocket server URI should also be passed as a parameter in this command inorder to publish task statuses to the rest of the RMF entities.

```bash
#minimal required parameters
ros2 run oro_fleet_adapter fleet_adapter -c CONFIG_FILE -n NAV_GRAPH

#Usage with the websocket uri
ros2 run oro_fleet_adapter fleet_adapter -c CONFIG_FILE -n NAV_GRAPH -s SERVER_URI

# oro fleet manager has a launch file that can be used to run the fleet adapter with the required parameters, you can use it as shown below
ros2 launch oro_fleet_adapter fleet.andino.launch.xml
```

## Sumary
in order to execute the full simulation environment with the andino robot, you will need to have 3 separate terminals running the following commands:
1. `ros2 launch oro_fleet_adapter fleet.andino.sim.launch.xml` (to launch the gazebo simulation environment with the andino robot)
2. `$HOME/.inorbit/dist/scripts/start.sh` (to start the inorbit agent which will be the fleet manager of the andino robot)
3. `ros2 launch oro_fleet_adapter fleet.andino.launch.xml` (to launch the fleet adapter that will connect the andino robot to RMF and the Inorbit agent)

# Docker

To build the docker image for this package, use the command below from the root of the repository.

```bash
./docker/build.sh
```

After building the image, you can use docker compose to run all the necessary services such as:
- oro_fleet_adapter
- open_rmf_web (frontend)
- open_rmf_server (backend)
- mock_api_server (to simulate the Inorbit api responses)

```bash
docker compose -f docker/docker-compose.yaml up -d
```

And open a web browser and navigate to `http://localhost:3000/robots` to access the RMF web interface and see the robot in action.