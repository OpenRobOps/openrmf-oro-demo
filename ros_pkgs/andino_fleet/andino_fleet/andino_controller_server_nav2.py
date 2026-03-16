import math
import time

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy import executors
from rclpy.action import ActionServer, CancelResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.logging import LoggingSeverity
from rclpy.node import Node
from tf_transformations import euler_from_quaternion
from typing import List
from geometry_msgs.msg import PoseStamped

import rclpy

from controller_action_msg.action import AndinoController
from controller_action_msg.msg import RobotPose

class AndinoControllerServer(Node):
    
    def __init__(self, node_name: str = 'andino_controller_node', *, context: rclpy.Context = None, cli_args: rclpy.List[str] = None, namespace: str = None, use_global_arguments: bool = True, enable_rosout: bool = True, start_parameter_services: bool = True, parameter_overrides: rclpy.List[rclpy.Parameter] = None, allow_undeclared_parameters: bool = False, automatically_declare_parameters_from_overrides: bool = False) -> None:
        super().__init__(node_name)
        rclpy.logging.set_logger_level(self.get_name(), LoggingSeverity.INFO)
        self._action_server = ActionServer(self,AndinoController,'andino_controller',self._execute_callback, cancel_callback=self._cancel_callback)

        # odom topic
        self._odom_sub = self.create_subscription(Odometry,'/odom',self._odom_callback,50)
        # velocity topic
        self._vel_pub = self.create_publisher(Twist,'/cmd_vel',10)
        # current pose topic
        self._pose_pub = self.create_publisher(RobotPose, '/current_pose', 10)
        
        # nav2 "rviz style" goal topic
        self._nav2_goal_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)

        # (optional) frame to use for nav2 goals
        self.declare_parameter('nav2_goal_frame', 'map')
        self.declare_parameter('distance_tolerance', 4.0)

        self._initialize_state()
        self.get_logger().info('Andino Controller Server Started')
    
    # This function to ensure all state vars exist
    def _initialize_state(self):
        self._curr_x = 0.0
        self._curr_y = 0.0
        self._yaw = 0.0
        self._quat_tf = [0.0, 0.0, 0.0, 0.0]

    # This callback is called by the action server to execute tasks for a specific goal handle
    def _execute_callback(self, goal_handle: ServerGoalHandle):
        self.get_logger().info('Sending goal to Nav2 via /goal_pose ...')

        goal_pose: PoseStamped = goal_handle.request.goal_pose

        # Ensure it has a frame_id Nav2 understands (usually "map")
        nav2_frame = self.get_parameter('nav2_goal_frame').get_parameter_value().string_value
        if not goal_pose.header.frame_id:
            goal_pose.header.frame_id = nav2_frame
        goal_pose.header.stamp = self.get_clock().now().to_msg()

        # Publish to Nav2
        self._nav2_goal_pub.publish(goal_pose)

        # --- Optional: keep sending *your* action feedback while Nav2 moves ---
        feedback = AndinoController.Feedback()
        tol = self.get_parameter('distance_tolerance').get_parameter_value().double_value

        gx = goal_pose.pose.position.x
        gy = goal_pose.pose.position.y
        
        self.get_logger().info(
            f'Sent goal {gx}, {gy} to Nav2. '
            'Now monitoring distance to goal and sending '
            f'feedback until within tolerance of {tol} m ...'
        )

        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                # IMPORTANT: With /goal_pose topic only, you cannot cancel Nav2.
                # You can only cancel *your* action and stop publishing feedback.
                self.get_logger().warn("Cancel requested. Cancelling AndinoController action, but Nav2 will keep going (topic goals can't be cancelled).")
                goal_handle.canceled()
                result = AndinoController.Result()
                result.success = False
                return result

            # distance remaining based on odom
            dx = gx - self._curr_x
            dy = gy - self._curr_y
            rho = math.sqrt(dx*dx + dy*dy)

            feedback.current_pose.header.stamp = self.get_clock().now().to_msg()
            feedback.current_pose.pose.position.x = self._curr_x
            feedback.current_pose.pose.position.y = self._curr_y
            feedback.current_pose.pose.position.z = 0.0
            feedback.current_pose.pose.orientation.x = self._quat_tf[0]
            feedback.current_pose.pose.orientation.y = self._quat_tf[1]
            feedback.current_pose.pose.orientation.z = self._quat_tf[2]
            feedback.current_pose.pose.orientation.w = self._quat_tf[3]
            feedback.distance_remaining = rho

            # Publish feedback
            goal_handle.publish_feedback(feedback)

            if rho <= tol:
                break

            time.sleep(0.1)

        goal_handle.succeed()
        result = AndinoController.Result()
        result.success = True
        return result

    def _cancel_callback(self, goal_handle: ServerGoalHandle):
        self.get_logger().info('Received cancel request :(')
        return CancelResponse.ACCEPT

    def _odom_callback(self,msg: Odometry):
        self._curr_x = msg.pose.pose.position.x
        self._curr_y = msg.pose.pose.position.y
        # orientation
        quat_tf = [msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w]
        (_, _, self._yaw, self._quat_tf) = self._quaternion_to_euler(quat_tf)

        # publish current pose
        self.publish_pose()
        self.get_logger().debug(f'[Odom] Current X: {self._curr_x} m | Current Y: {self._curr_y} m | Yaw:{self._yaw} rad')

    def _quaternion_to_euler(self, quaternion: List) -> tuple:
        (roll,pitch,yaw) = euler_from_quaternion(quaternion)
        return (roll,pitch,yaw,quaternion)
    
    def _normalize_angle(self, theta) -> float:
        '''
        Normalize theta(radian) to be between (-pi,pi]
        '''
        norm_theta = theta
        while norm_theta < (-1) * math.pi: norm_theta += 2*math.pi
        while norm_theta >= math.pi: norm_theta -= 2*math.pi
        return norm_theta

    def _update_rho(self, x: float, y: float) -> float:
        rho = math.sqrt(x**2 + y**2)
        return rho
    
    def _update_alpha(self, x: float, y: float, theta: float) -> float:
        alpha = (-1)*theta + math.atan2(y,x)
        return self._normalize_angle(alpha)
    
    def _update_beta(self, alpha:float, theta: float) -> float:
        beta = (-1)*theta - alpha
        return self._normalize_angle(beta)
    
    def _update_states(self, x_goal : float, y_goal: float) -> tuple:
        delta_x = x_goal - self._curr_x
        delta_y = y_goal - self._curr_y
        theta = self._yaw
        return (delta_x,delta_y,theta)
    
    def _update_topic_names(self) -> str:
        topic_names_and_types = self.get_topic_names_and_types()
        namespace = self.get_namespace()
        topic = namespace+'/current_pose'
        for name, type in topic_names_and_types:
            if topic in name:
                return name
        return ''
    
    def stop_robot(self):
        vel_msg = Twist()
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = 0.0

        self._vel_pub.publish(vel_msg)


    def publish_pose(self):
        pose_msg = RobotPose()
        pose_msg.topic_name = self._update_topic_names()
        pose_msg.current_pose = [self._curr_x, self._curr_y, self._yaw]

        self._pose_pub.publish(pose_msg)

def main(args=None):
    rclpy.init(args=args)

    andino_server = AndinoControllerServer('andino_controller_server')

    executor = executors.MultiThreadedExecutor()
    executor.add_node(andino_server)

    try:
        executor.spin()
    except KeyboardInterrupt:
        andino_server.destroy_node()
        andino_server.get_logger().info('KeyboardInterrupt. Shutting Down...')
    
if __name__== '__main__':
    main()
