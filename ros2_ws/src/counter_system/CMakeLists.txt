cmake_minimum_required(VERSION 3.8)

project(counter_system)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

find_package(rosidl_default_generators REQUIRED)

#
# Generate Service
#
rosidl_generate_interfaces(
  ${PROJECT_NAME}
  "srv/ResetCounter.srv"
)

#
# Publisher
#
add_executable(
  publisher_node
  src/publisher_node.cpp
)

ament_target_dependencies(
  publisher_node
  rclcpp
  std_msgs
)

#
# Subscriber
#
add_executable(
  subscriber_node
  src/subscriber_node.cpp
)

ament_target_dependencies(
  subscriber_node
  rclcpp
  std_msgs
)

#
# Link generated service headers
#
rosidl_get_typesupport_target(
  cpp_typesupport_target
  ${PROJECT_NAME}
  "rosidl_typesupport_cpp"
)

target_link_libraries(
  publisher_node
  ${cpp_typesupport_target}
)

target_link_libraries(
  subscriber_node
  ${cpp_typesupport_target}
)

#
# Install
#
install(
  TARGETS
    publisher_node
    subscriber_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_export_dependencies(
  rosidl_default_runtime
)

ament_package()