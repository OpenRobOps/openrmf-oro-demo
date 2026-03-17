# Copyright 2021 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""The RobotAPI class is a wrapper for API calls to the robot.

Here users are expected to fill up the implementations of functions which will
be used by the RobotCommandHandle. For example, if your robot has a REST API,
you will need to make http request calls to the appropriate endpoints within
these functions.
"""

from rclpy.impl.rcutils_logger import RcutilsLogger

from .Requester import Requester


class RobotAPI:
    # The constructor below accepts parameters typically required to submit
    # http requests. Users should modify the constructor as per the
    # requirements of their robot's API
    def __init__(self, prefix: str, timeout: float, api_key: str, battery_attribute_id: str, map_attribute_id: str):
        self.prefix = prefix
        self.timeout = timeout
        self.logger = RcutilsLogger(f"RobotAPI ({prefix})")
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-auth-inorbit-app-key": api_key,
        }
        self.battery_attribute_id = battery_attribute_id
        self.map_attribute_id = map_attribute_id
        self.requester = Requester(base_url=self.prefix, headers=self.headers, timeout=self.timeout, logger=self.logger)
        self.last_activity_id = None

    def get_robot_id(self, robot_name: str) -> str:
        """Extracts the last part of a robot name split by underscore.

        Example: 'andino_123' -> '123'
        """
        return robot_name.split("_")[-1]

    def check_connection(self):
        """Return True if connection to the robot API server is successful"""
        response = self.requester.get_request(endpoint="robots")
        if response is None:
            self.logger.error("No response received from robot API server")
            return False
        return True

    def is_command_completed(self, robot_name: str):
        """Return True if the robot has completed its last command, else

        return False.
        """
        robot_name = self.get_robot_id(robot_name)
        if self.last_activity_id is None:
            self.logger.info(f"No last activity recorded for robot '{robot_name}'")
            return True
        response = self.requester.get_request(endpoint=f"robots/{robot_name}/actions/{self.last_activity_id}")
        response_json = response.json()

        if response is None:
            self.logger.error("No response received from robot API server")
            return False

        if response_json.get("status", None) == "finished":
            self.logger.info(f"Activity '{self.last_activity_id}' for robot '{robot_name}' has completed")
            self.last_activity_id = None
            return True
        return False

    def navigate(
        self,
        robot_name: str,
        pose,
        map_name: str,
        speed_limit=0.0,
    ):
        """Request the robot to navigate to pose:[x,y,theta].

        Where x, y and theta are in the robot's coordinate convention.
        This function should return True if the robot has accepted the request,
        else False.
        """
        robot_name = self.get_robot_id(robot_name)
        self.logger.info(
            f"Received navigation request for {robot_name} to pose "
            f"{pose} on map {map_name} with speed limit {speed_limit}"
        )

        request_body = {
            "waypoints": [
                {
                    "frameId": map_name,
                    "x": pose[0],
                    "y": pose[1],
                    "theta": pose[2],
                }
            ]
        }
        response = self.requester.post_request(endpoint=f"robots/{robot_name}/navigation/waypoints", json=request_body)
        if response is None:
            self.logger.error("No response received from robot API server")
            return False
        return response.status_code == self.requester.HTTP_OK

    def localize(
        self,
        robot_name: str,
        pose,
        map_name: str,
    ):
        """Request the robot to localize on target map. This

        function should return True if the robot has accepted the
        request, else False
        """
        # TODO: currently the localization uses a delta pose to update the
        # robot's position.We just change the sign of the input pose to make
        # it a delta pose. This is because the robot's API only supports
        # relative localization. If the robot's API supports directly setting
        # the robot's pose, we can modify this function to use that instead.
        robot_name = self.get_robot_id(robot_name)
        action_body = {
            "actionId": "Relocalize-000000",
            "parameters": {"deltaPose": {"x": -pose[0], "y": -pose[1], "theta": -pose[2], "frameId": map_name}},
        }
        response = self.requester.post_request(endpoint=f"robots/{robot_name}/actions", json=action_body)
        if response is None:
            self.logger.error("No response received from robot API server")
            return False
        return response.status_code == self.requester.HTTP_OK

    def start_activity(self, robot_name: str, activity: str, label: str, activity_args: dict | None = None):
        """Request the robot to begin a process.

        This is specific to the robot and the use case.
        For example, load/unload a cart for Deliverybot
        or begin cleaning a zone for a cleaning robot.
        """
        robot_name = self.get_robot_id(robot_name)
        action_body = {"actionId": f"{activity}", "parameters": activity_args}
        response = self.requester.post_request(endpoint=f"robots/{robot_name}/actions", json=action_body)
        if response is None:
            self.logger.error("No response received from robot API server")
            return False
        response_json = response.json()
        self.logger.info(f"Activity started for robot {robot_name}: {activity} with response: {response_json}")
        self.last_activity_id = response_json.get("executionId", None)
        return response.status_code == self.requester.HTTP_OK

    def stop(self, robot_name: str):
        """Command the robot to stop.

        Return True if robot has successfully stopped. Else False.
        """
        if self.last_activity_id is None:
            self.logger.error(f"No last activity recorded for robot '{robot_name}'. Cannot stop.")
            return True
        robot_name = self.get_robot_id(robot_name)
        action_body = {"actionId": self.last_activity_id, "parameters": {}}
        response = self.requester.post_request(endpoint=f"robots/{robot_name}/actions", json=action_body)
        if response is None:
            self.logger.error("No response received from robot API server")
            return False
        self.last_activity_id = None
        return response.status_code == self.requester.HTTP_OK

    def position(self, robot_name: str):
        robot_name = self.get_robot_id(robot_name)
        """ Return [x, y, theta] expressed in the robot's coordinate frame or
        None if any errors are encountered """

        response = self.requester.get_request(endpoint=f"robots/{robot_name}/localization/pose")
        if response is None:
            self.logger.error("No response received from robot API server")
            return None
        response_json = response.json()

        # check if response_json has the expected keys x, y, theta
        if not all(k in response_json for k in ("x", "y", "theta")):
            self.logger.error(f"Response JSON missing expected keys: {response_json}")
            return None
        return [float(response_json["x"]), float(response_json["y"]), float(response_json["theta"])]

    def battery_soc(self, robot_name: str):
        """Return the state of charge of the robot as a value between 0.0

        and 1.0. Else return None if any errors are encountered.
        """
        robot_name = self.get_robot_id(robot_name)
        attribute_id = self.battery_attribute_id
        response = self.requester.get_request(endpoint=f"robots/{robot_name}/attributes/{attribute_id}")
        if response is None:
            self.logger.error("No response received from robot API server")
            return None
        response_json = response.json()
        # check if response_json has the expected key 'value'
        if "value" not in response_json:
            self.logger.error(f"Response JSON missing 'value' key: {response_json}")
            return None
        # check that the battery soc value is between 0.0 and 1.0
        if response_json["value"] == "":
            self.logger.error(f"Battery SoC value is empty string: {response_json}")
            return None
        if not (0.0 <= float(response_json["value"]) <= 1.0):
            self.logger.error(f"Battery SoC value out of expected range [0.0, 1.0]: {response_json['value']}")
            return None
        return float(response_json["value"])

    def map(self, robot_name: str):
        """Return the name of the map that the robot is currently on or

        None if any errors are encountered.
        """
        robot_name = self.get_robot_id(robot_name)
        response = self.requester.get_request(endpoint=f"robots/{robot_name}/attributes/{self.map_attribute_id}")
        if response is None:
            self.logger.error("No response received from robot API server")
            return None
        response_json = response.json()

        # check if response_json has the expected key 'value'
        if "value" not in response_json:
            self.logger.error(f"Response JSON missing 'value' key: {response_json}")
            return None
        return response_json["value"]

    def get_data(self, robot_name: str | None = None):
        """Return a RobotUpdateData for one robot if a name is given.

        Otherwise return a list of RobotUpdateData for all robots.
        """
        map = self.map(robot_name)
        position = self.position(robot_name)
        battery_soc = self.battery_soc(robot_name)
        if not (map is None or position is None or battery_soc is None):
            return RobotUpdateData(robot_name, map, position, battery_soc)
        return None


class RobotUpdateData:
    """Update data for a single robot."""

    def __init__(
        self, robot_name: str, map: str, position: list[float], battery_soc: float, requires_replan: bool | None = None
    ):
        self.robot_name = robot_name
        x = position[0]
        y = position[1]
        yaw = position[2]
        self.position = [x, y, yaw]
        self.map = map
        self.battery_soc = battery_soc
        self.requires_replan = requires_replan
