#!/bin/bash

set -e

source /opt/ros/humble/setup.bash
source /ws/install/setup.bash

exec uvicorn app:app --host 0.0.0.0 --port 8000
