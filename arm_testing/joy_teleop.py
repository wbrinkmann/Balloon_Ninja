#!/usr/bin/env python3

"""mostly generated with chat to see if we can 
communicate with arm in initial phase"""

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Joy, JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


class JoyArmTeleop(Node):

    def __init__(self):
        super().__init__('joy_arm_teleop')

        self.joint_names = [
            'joint_1', 'joint_2', 'joint_3',
            'joint_4', 'joint_5', 'joint_6'
        ]

        self.joint_positions = None
        self.target_positions = None

        self.joy_axes = [0.0] * 8
        self.joy_buttons = []

        self.last_joy_time = self.get_clock().now()
        self.enabled = False

        # Movement settings
        self.speed = 0.12
        self.max_offset = 0.35
        self.deadzone = 0.12

        # Controller mapping
        self.enable_button = 4  # L1

        # D-pad axis placeholders (identify using /joy)
        self.dpad_vertical_axis = 7

        # X and A button placeholders (identify using /joy)
        self.joint_6_up_button = 3    # X
        self.joint_6_down_button = 0  # A

        self.joy_sub = self.create_subscription(
            Joy, '/joy', self.joy_callback, 10
        )

        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_callback, 10
        )

        self.command_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )

        self.timer = self.create_timer(0.05, self.control_loop)

        self.get_logger().info('Joystick teleop initialized.')
        self.get_logger().info('Hold L1 to enable movement.')

    def joint_callback(self, msg):
        positions = dict(zip(msg.name, msg.position))

        if all(name in positions for name in self.joint_names):
            self.joint_positions = [
                positions[name] for name in self.joint_names
            ]

            if self.target_positions is None:
                self.target_positions = self.joint_positions.copy()
                self.get_logger().info('Received initial joint positions.')

    def joy_callback(self, msg):
        self.joy_axes = list(msg.axes)
        self.joy_buttons = list(msg.buttons)
        self.last_joy_time = self.get_clock().now()

    def get_axis(self, index):
        if index is None or index >= len(self.joy_axes):
            return 0.0

        value = self.joy_axes[index]

        if abs(value) < self.deadzone:
            return 0.0

        return value

    def get_button(self, index):
        if index is None or index >= len(self.joy_buttons):
            return False

        return self.joy_buttons[index] == 1

    def publish_trajectory(self):
        msg = JointTrajectory()
        msg.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = self.target_positions
        point.time_from_start.sec = 0
        point.time_from_start.nanosec = 150_000_000

        msg.points.append(point)
        self.command_pub.publish(msg)

    def control_loop(self):
        if self.joint_positions is None:
            return

        if self.target_positions is None:
            return

        joy_age = (
            self.get_clock().now() - self.last_joy_time
        ).nanoseconds / 1e9

        if joy_age > 0.5:
            self.enabled = False

        enable = (
            self.get_button(self.enable_button)
            and joy_age <= 0.5
        )

        if not enable:
            if self.enabled:
                self.target_positions = self.joint_positions.copy()
                self.publish_trajectory()

            self.enabled = False
            return

        self.enabled = True

        # Joint 1-4: analog sticks
        commands = [
            -self.get_axis(1),  # Joint 1: left stick up/down
            self.get_axis(0),   # Joint 2: left stick left/right
            -self.get_axis(4),  # Joint 3: right stick up/down
            -self.get_axis(3),  # Joint 4: right stick left/right
            0.0,                # Joint 5: D-pad
            0.0                 # Joint 6: X/A buttons
        ]

        # Joint 5: D-pad up/down
        commands[4] = self.get_axis(self.dpad_vertical_axis)

        # Joint 6: X/A buttons
        if self.get_button(self.joint_6_up_button):
            commands[5] = 1.0
        elif self.get_button(self.joint_6_down_button):
            commands[5] = -1.0

        # Integrate joystick inputs into joint positions
        dt = 0.05

        for i in range(6):
            change = commands[i] * self.speed * dt

            starting_position = self.joint_positions[i]
            proposed_position = self.target_positions[i] + change

            lower = starting_position - self.max_offset
            upper = starting_position + self.max_offset

            self.target_positions[i] = max(
                lower, min(upper, proposed_position)
            )

        self.publish_trajectory()


def main(args=None):
    rclpy.init(args=args)

    node = JoyArmTeleop()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()