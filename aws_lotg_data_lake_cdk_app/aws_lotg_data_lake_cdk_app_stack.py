from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_ecs_patterns as ecsp,
)
from constructs import Construct

class AwsLotgDataLakeCdkAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Task definition
        lotg_taskdef = ecs.FargateTaskDefinition(self, "lotg-taskdef",
                cpu=256,
                memory_limit_mib=512,
                )

        # Task role allow writing to Firehose (Kinesis Delivery Streams)
        lotg_taskdef.add_to_task_role_policy(
                iam.PolicyStatement(
                    actions=["firehose:PutRecordBatch"],
                    resources=["*"],
                    )
                )

         # App container
        lotg_app_container = lotg_taskdef.add_container(
                "lotg_app",
                image=ecs.ContainerImage.from_registry("nginx"),
                logging=ecs.LogDrivers.firelens(
                    options={
                        "Name": "firehose",
                        "region": "ap-southeast-1",
                        "delivery_stream": "learn-on-the-go-real-time-data-stream",
                        },
                    ),
                port_mappings=[ecs.PortMapping(container_port=80)],
                memory_reservation_mib= 100,
                )

       # Firelens config
        lotg_firelens_config = ecs.FirelensConfig(
                type=ecs.FirelensLogRouterType.FLUENTBIT)

        # Firelens sidecar
        lotg_firelens_container = lotg_taskdef.add_firelens_log_router(
                "lotg_log_router",
                firelens_config=lotg_firelens_config,
                image=ecs.ContainerImage.from_registry("amazon/aws-for-fluent-bit"),
                logging=ecs.LogDriver.aws_logs(
                    stream_prefix="firelens",
                    ),
                memory_reservation_mib=50,
                )

        # Add dependsOn FireLens lotg_log_router container
        lotg_app_container.add_container_dependencies(
                ecs.ContainerDependency(
                    container=lotg_firelens_container,
                    condition=ecs.ContainerDependencyCondition.START,
                    )
                )

        # Putting it all together
        lotg_service = ecsp.ApplicationLoadBalancedFargateService(
                self,
                "lotg-service",
                cpu=512,
                desired_count=1,
                task_definition=lotg_taskdef,
                memory_limit_mib=2048,
                public_load_balancer=True,
                )
