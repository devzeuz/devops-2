# Blue/Green Deployment with Observability & Slack Alerts

This repository provides a **Blue/Green deployment setup** for a Node.js service using **Nginx reverse proxy**, a **Python log watcher**, and **Slack alerting** for failovers and high error rates.

---

## Table of Contents

- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Starting Services](#starting-services)
- [Chaos Testing](#chaos-testing)
  - [Failover Test](#failover-test)
  - [High Error-Rate Test](#high-error-rate-test)
- [Viewing Logs](#viewing-logs)

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/<your-username>/devops-2.git
cd devops-2

2.  Create and configure the .env file
    cp .env.example .env

3. **Update the following values in .env (especially SLACK_WEBHOOK_URL)**
    BLUE_IMAGE=yimikaade/wonderful:devops-stage-two
GREEN_IMAGE=yimikaade/wonderful:devops-stage-two
ACTIVE_POOL=blue
PORT=8080
RELEASE_ID_BLUE=v1-blue
RELEASE_ID_GREEN=v1-green
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T09AMR8A/B09PCJJQWovrMqe7gJLnLrM
ERROR_RATE_THRESHOLD=2
WINDOW_SIZE=200
ALERT_COOLDOWN_SEC=300
MAINTENANCE_MODE=0

4. Run all services using Docker Compose:
   docker compose up -d

**Failover Test**

1. Cause the Blue service to fail: curl -X POST http://localhost:8081/chaos/start?mode=error
2. Check if Nginx reroutes traffic to Green: curl -i http://localhost:8080/version
3. curl -X POST http://localhost:8081/chaos/stop


**High Error-Rate Test**
Make test_failover_alert.sh executable by running chmod +x test_failover.sh then run it: ./test_failover_alert.sh when that is done, check your slack.


![Failover Test Screenshot](https://images-8989897776633.s3.us-east-1.amazonaws.com/Screenshot+2025-10-31+at+7.25.08%E2%80%AFAM.png)

![High Error Rate Screenshot](https://images-8989897776633.s3.us-east-1.amazonaws.com/Screenshot+2025-10-31+at+7.30.10%E2%80%AFAM.png)


**Viewing Logs**
Nginx logs (includes pool, release, upstream status, latency, etc.):  docker exec nginx tail -n 50 /var/log/nginx/access.log

