import ros_bridge


def test_start_is_noop_without_ros():
    ros_bridge.start()

    assert ros_bridge._ROS_AVAILABLE is False
    assert ros_bridge._node is None


def test_reset_counter_without_node_returns_false():
    assert ros_bridge.reset_counter() is False
