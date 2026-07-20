import threading
import time

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import Int32

    from counter_system.srv import ResetCounter

    _ROS_AVAILABLE = True

except ImportError:
    _ROS_AVAILABLE = False

publisher_value = 0
subscriber_value = 0

publisher_alive = False
subscriber_alive = False

_LIVELINESS_TIMEOUT = 3.0

_last_message_time = 0.0

_node = None


if _ROS_AVAILABLE:  # pragma: no cover -- exercised only in the ROS-enabled container

    class CounterBridge(Node):

        def __init__(self):
            super().__init__("fastapi_bridge")

            self._subscription = self.create_subscription(
                Int32, "/counter", self._on_counter, 10
            )

            self._reset_client = self.create_client(
                ResetCounter, "/reset_counter"
            )

            self.create_timer(1.0, self._check_liveliness)

        def _on_counter(self, msg):
            global publisher_value, subscriber_value, _last_message_time

            publisher_value = msg.data
            subscriber_value = msg.data
            _last_message_time = time.monotonic()

        def _check_liveliness(self):
            global publisher_alive, subscriber_alive

            fresh = (time.monotonic() - _last_message_time) < _LIVELINESS_TIMEOUT

            publisher_alive = fresh
            subscriber_alive = fresh and "subscriber_node" in self.get_node_names()

        def call_reset(self):
            if not self._reset_client.wait_for_service(timeout_sec=2.0):
                return False

            future = self._reset_client.call_async(ResetCounter.Request())

            event = threading.Event()
            future.add_done_callback(lambda _: event.set())

            if not event.wait(timeout=2.0):
                return False

            result = future.result()

            return bool(result and result.success)


def start():
    global _node

    if not _ROS_AVAILABLE:
        return

    rclpy.init()  # pragma: no cover -- exercised only in the ROS-enabled container
    _node = CounterBridge()  # pragma: no cover

    threading.Thread(  # pragma: no cover
        target=rclpy.spin, args=(_node,), daemon=True
    ).start()


def reset_counter():
    if _node is None:
        return False

    return _node.call_reset()
