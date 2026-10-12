"""Chaos Engineering Task Termination Experiment.

Injects synthetic faults by stopping random ECS tasks during traffic shifts
to prove ALB connection draining and zero-downtime resilience.
"""

import argparse
import random
import sys
import time
import urllib.request
import boto3

def run_chaos_experiment(cluster_name: str, service_name: str, alb_url: str):
    print(f"Starting Chaos Experiment on ECS Cluster: {cluster_name}")
    ecs = boto3.client("ecs")

    # Step 1: List active tasks
    tasks = ecs.list_tasks(cluster=cluster_name, serviceName=service_name).get("taskArns", [])
    if not tasks:
        print("No active tasks found to inject chaos. Exiting safely.")
        return

    target_task = random.choice(tasks)
    print(f"Selecting target task for failure injection: {target_task}")

    # Step 2: Concurrently query ALB endpoint
    failures = 0
    successes = 0

    print("Sending traffic during task termination...")
    ecs.stop_task(cluster=cluster_name, task=target_task, reason="Chaos Engineering Resiliency Test")

    start = time.time()
    while time.time() - start < 15:
        try:
            req = urllib.request.Request(f"{alb_url}/health")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    successes += 1
                else:
                    failures += 1
        except Exception:
            failures += 1
        time.sleep(0.2)

    print(f"Chaos Result -> Successes: {successes}, Failures: {failures}")
    if failures == 0:
        print("RESILIENCY VALIDATED: Zero 5xx errors recorded during task termination.")
    else:
        print(f"WARNING: Detected {failures} dropped connections during container drain.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster", default="cicd-demo-cluster")
    parser.add_argument("--service", default="cicd-demo-prod")
    parser.add_argument("--url", default="http://localhost:8080")
    args = parser.parse_args()
    run_chaos_experiment(args.cluster, args.service, args.url)
