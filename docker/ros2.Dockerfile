FROM ros:humble

WORKDIR /ws

COPY ros2_ws /ws

RUN . /opt/ros/humble/setup.sh && \
    colcon build

CMD bash