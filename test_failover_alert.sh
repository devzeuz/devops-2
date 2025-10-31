#!/usr/bin/env bash
set -euo pipefail

echo "=== Stage 3: Failover Alert Test ==="

# Step 1: Check baseline (Blue should be active)
echo "Baseline (should be Blue):"
curl -i http://localhost:8080/version | grep -E 'X-App-Pool|X-Release-Id'

# Step 2: Start chaos on Blue to simulate failure
echo "Starting chaos on Blue..."
curl -s -X POST "http://localhost:8081/chaos/start?mode=error" || true
sleep 1

# Step 3: Trigger requests to Nginx to exercise failover
echo "Sending 10 requests through Nginx to trigger failover..."
for i in {1..10}; do
  curl -s -i http://localhost:8080/version | grep -E 'X-App-Pool|X-Release-Id'
done

# Step 4: Stop chaos on Blue
echo "Stopping chaos on Blue..."
curl -s -X POST "http://localhost:8081/chaos/stop" || true

echo "Failover alert test complete. Check Slack for failover notification."

