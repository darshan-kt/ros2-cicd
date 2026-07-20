#!/bin/bash

set -e

echo "==================================="
echo "ROS2 Container Starting"
echo "==================================="

source /opt/ros/humble/setup.bash

echo ""
echo "ROS Environment Loaded"
echo ""

if [ ! -f /ws/install/setup.bash ]; then
    echo "ERROR: /ws/install/setup.bash not found"
    echo "Workspace build failed"
    exit 1
fi

source /ws/install/setup.bash

echo ""
echo "Available Packages:"
ros2 pkg list | grep counter || true
echo ""

echo "Starting Publisher..."
ros2 run counter_system publisher_node &
PUB_PID=$!

sleep 2

echo "Starting Subscriber..."
ros2 run counter_system subscriber_node &
SUB_PID=$!

echo ""
echo "ROS2 Nodes Started"
# echo "Publisher PID: $PUB_PID"
# echo "Subscriber PID: $SUB_PID"
echo ""

wait $PUB_PID $SUB_PID