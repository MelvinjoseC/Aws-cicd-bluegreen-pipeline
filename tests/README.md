# Performance & Reliability Test Suite

This directory contains automated stress and reliability test suites for evaluating AWS ECS Blue/Green pipeline resiliency.

### 1. Locust Performance & Auto-scaling Test
```bash
# Run headless stress test with 50 concurrent workers
locust -f tests/locustfile.py --host="http://<ALB_DNS>" --headless -u 50 -r 10 --run-time 2m
```

### 2. Chaos Engineering Fault Injection Test
```bash
# Simulate random ECS task termination during active traffic shift
python tests/chaos_test.py --cluster cicd-demo-cluster --service cicd-demo-prod
```
