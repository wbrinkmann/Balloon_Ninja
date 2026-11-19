# Setup


## Kinova Arm Setup
For Kinova gen3_lite.
Adapted from Kinova. [Their repo.](https://github.com/Kinovarobotics/ros2_kortex/tree/jazzy)

1. Make sure that `colcon`, its extensions, and `vcs` are installed:

        sudo apt install python3-colcon-common-extensions python3-vcstool

2. Clone their repo in your `ros2_ws/src`

        git clone https://github.com/Kinovarobotics/ros2_kortex.git 

3. Make sure you are in `jazzy` branch. 

        # check branch
        git branch --show-current

        # switch to jazzy if not jazzy
        git switch jazzy

4. Navigate back to workspace. Pull relevant packages

        vcs import src --skip-existing --input src/ros2_kortex/ros2_kortex.$ROS_DISTRO.repos
        vcs import src --skip-existing --input src/ros2_kortex/ros2_kortex-not-released.$ROS_DISTRO.repos

    Pull gazebo simulation packages

        vcs import src --skip-existing --input src/ros2_kortex/simulation.jazzy.repos

5. Install dependencies

        rosdep install --ignore-src --from-paths src -y -r

6. Build and source

        colcon build --symlink-build
        source install/setup.bash

## Initial Arm Connection with Joystick Teleop
1. Install joystick packages

        sudo apt install ros-jazzy-joy

    check if it works, run in two seperate terminals

        ros2 run joy joy_node
        ros2 topic echo /joy

2. Clone our repo to `ros2_ws/src`

3. To test in sim, run in seperate terminals

        # connect to arm in sim
        ros2 launch kortex_bringup gen3_lite.launch.py \
        robot_ip:=yyy.yyy.yyy.yyy \
        use_fake_hardware:=true

        # connect to controller (we used logitech controller)
        ros2 run joy joy_node

        # run script to communicate between nodes
        python3 src/Balloon_Tracking/arm_testing/joy_teleop.py

4. To test on real arm hardware, run in seperate terminals

        # connect to arm 
        ros2 launch kortex_bringup gen3_lite.launch.py robot_ip:=192.168.1.10 

        # connect to controller (we used logitech controller)
        ros2 run joy joy_node

        # run script to communicate between nodes
        python3 src/Balloon_Tracking/arm_testing/joy_teleop.py

**Teleop only sends with deadman's switch. Press L1 to send messages.**

