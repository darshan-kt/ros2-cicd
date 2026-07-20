FROM ros:humble

WORKDIR /ws

COPY ros2_ws /ws

RUN bash -c "source /opt/ros/humble/setup.bash && colcon build"

COPY docker/start_ros.sh /start_ros.sh

RUN chmod +x /start_ros.sh

CMD ["/start_ros.sh"]