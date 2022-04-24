import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_lotg_data_lake_cdk_app.aws_lotg_data_lake_cdk_app_stack import AwsLotgDataLakeCdkAppStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_lotg_data_lake_cdk_app/aws_lotg_data_lake_cdk_app_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsLotgDataLakeCdkAppStack(app, "aws-lotg-data-lake-cdk-app")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
