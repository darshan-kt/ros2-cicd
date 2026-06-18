#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/int32.hpp"

class SubscriberNode : public rclcpp::Node
{
public:

    SubscriberNode()
        : Node("subscriber_node")
    {
        subscription_ =
            create_subscription<std_msgs::msg::Int32>(
                "/counter",
                10,
                std::bind(
                    &SubscriberNode::callback,
                    this,
                    std::placeholders::_1));
    }

private:

    void callback(
        const std_msgs::msg::Int32::SharedPtr msg)
    {
        latest_value_ = msg->data;

        RCLCPP_INFO(
            get_logger(),
            "Received: %d",
            latest_value_);
    }

    int latest_value_{0};

    rclcpp::Subscription<
        std_msgs::msg::Int32>::SharedPtr subscription_;
};

int main(int argc,char ** argv)
{
    rclcpp::init(argc,argv);

    rclcpp::spin(
        std::make_shared<SubscriberNode>());

    rclcpp::shutdown();

    return 0;
}