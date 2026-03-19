# Simulation Config

This directory contains the configuration files for the simulation of the OpenRMF ORO demo. It includes the `docker-compose.yaml` file that defines the services and their configurations, as well as the `entrypoint.sh` script that initializes the fleet adapter service.

## ORO configuration

if this is the first time executing this and the robot is not on the ORO platform, you need to create the robot using the connect robot. this will give you the liffoff key, an example of this url is `curl https://control.inorbit.ai/liftoff/mwZZ50wpoCOh33bMS | sh` where `mwZZ50wpoCOh33bMS` is the liftoff key. you need to add this key to the env on the docker container as `INORBIT_LIFTOFF_KEY`. This will allow the fleet adapter to connect to the ORO platform and receive commands for the robot.

> Note: If you dont know the robot id, you can delete `INORBIT_ID` from the enviroment variables to assing a random id to the robot, execute the container with the agent and check the file `inorbit/agent.env.sh` to see what id was assigned check the file `inorbit/agent.env.sh`, to keep it just make sure `INORBIT_ID` has a value.

This simulation is running a node called `battery_fake` that is publishing to 2 custom topics to ORO, battery percentage and map name, check the package to do any change that you may need.