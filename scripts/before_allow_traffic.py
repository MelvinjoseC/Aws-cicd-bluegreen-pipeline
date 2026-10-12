# CodeDeploy Lifecycle Event Hook - BeforeAllowTraffic
# Executes smoke validations against green target group before any user traffic shifts

import json
import os
import urllib.request
import boto3

codedeploy = boto3.client("codedeploy")

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    deployment_id = event.get("DeploymentId")
    lifecycle_event_hook_execution_id = event.get("LifecycleEventHookExecutionId")

    alb_test_dns = os.environ.get("ALB_TEST_URL", "http://localhost:8443")
    health_url = f"{alb_test_dns}/livez"
    status = "Failed"

    try:
        req = urllib.request.Request(health_url, headers={"User-Agent": "CodeDeployHookValidator/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                body = json.loads(response.read().decode())
                if body.get("status") == "alive":
                    print("Green target group passed pre-traffic smoke checks.")
                    status = "Succeeded"
                else:
                    print("Unexpected response body:", body)
            else:
                print(f"Non-200 status code: {response.status}")
    except Exception as e:
        print(f"Validation request failed: {e}")

    if deployment_id and lifecycle_event_hook_execution_id:
        codedeploy.put_lifecycle_event_hook_execution_status(
            deploymentId=deployment_id,
            lifecycleEventHookExecutionId=lifecycle_event_hook_execution_id,
            status=status
        )
    return {"status": status}
