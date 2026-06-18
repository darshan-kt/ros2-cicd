#include <chrono>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/int32.hpp"

#include "counter_system/srv/reset_counter.hpp"

using namespace std::chrono_literals;

class PublisherNode : public rclcpp::Node
{
public:

    PublisherNode()
        : Node("publisher_node"),
          counter_(0)
    {
        publisher_ =
            create_publisher<std_msgs::msg::Int32>(
                "/counter",
                10);

        timer_ =
            create_wall_timer(
                1s,
                std::bind(
                    &PublisherNode::publish_counter,
                    this));

        reset_service_ =
            create_service<
                counter_system::srv::ResetCounter>(
                "/reset_counter",
                std::bind(
                    &PublisherNode::reset_callback,
                    this,
                    std::placeholders::_1,
                    std::placeholders::_2));

        RCLCPP_INFO(
            get_logger(),
            "Publisher started");
    }

private:

    void publish_counter()
    {
        auto msg =
            std_msgs::msg::Int32();

        msg.data = counter_;

        publisher_->publish(msg);

        RCLCPP_INFO(
            get_logger(),
            "Publishing: %d",
            counter_);

        counter_++;
    }

    void reset_callback(
        const std::shared_ptr<
            counter_system::srv::ResetCounter::Request>,
        std::shared_ptr<
            counter_system::srv::ResetCounter::Response> response)
    {
        counter_ = 0;

        response->success = true;

        RCLCPP_WARN(
            get_logger(),
            "Counter reset");
    }

    int counter_;

    rclcpp::Publisher<std_msgs::msg::Int32>::SharedPtr publisher_;

    rclcpp::TimerBase::SharedPtr timer_;

    rclcpp::Service<
        counter_system::srv::ResetCounter>::SharedPtr reset_service_;
};

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);

    rclcpp::spin(
        std::make_shared<PublisherNode>());

    rclcpp::shutdown();

    return 0;
}