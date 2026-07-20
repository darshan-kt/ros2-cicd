FROM ros:humble AS ros_build

WORKDIR /ws

COPY ros2_ws /ws

RUN bash -c "source /opt/ros/humble/setup.bash && colcon build"

FROM ros:humble

WORKDIR /app

COPY --from=ros_build /ws/install /ws/install

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend .

COPY docker/start_backend.sh /start_backend.sh

RUN chmod +x /start_backend.sh

CMD ["/start_backend.sh"]
