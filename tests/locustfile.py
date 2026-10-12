"""Distributed load testing suite for validating Blue/Green canary deployments and auto-scaling."""

import random
from locust import HttpUser, task, between


class BlueGreenLoadTestUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(60)
    def test_list_items(self):
        """Simulate high-volume API read traffic."""
        with self.client.get("/api/items", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status: {response.status_code}")

    @task(25)
    def test_index_route(self):
        """Simulate root landing page requests."""
        self.client.get("/")

    @task(10)
    def test_health_probe(self):
        """Simulate ALB health check probe traffic."""
        self.client.get("/health")

    @task(5)
    def test_diagnostic_telemetry(self):
        """Simulate operational dashboard telemetry polling."""
        self.client.get("/health/diagnostic")
