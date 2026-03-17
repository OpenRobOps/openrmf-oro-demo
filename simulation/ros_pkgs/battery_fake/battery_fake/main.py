import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class FakeBatteryNode(Node):
    def __init__(self):
        super().__init__('battery_fake')
        self.publisher_ = self.create_publisher(
            String, 
            '/inorbit/custom_data', 
            10
        )

        timer_period = 1.0 
        self.timer_battery = self.create_timer(timer_period, self.timer_callback)
        self.timer_map_label = self.create_timer(timer_period, self.map_label_callback)
        
        self.battery_level = 1.0  
        self.map_label = "L1"

    def timer_callback(self):
        msg = String()
        msg.data = f'battery={self.battery_level:.2f}'
        self.publisher_.publish(msg)
    
    def map_label_callback(self):
        msg = String()
        msg.data = f'map_label={self.map_label}'
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = FakeBatteryNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()