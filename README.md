# ROS2 Monitoring System

A full-stack ROS2 monitoring application built to demonstrate modern CI/CD practices using ROS2, FastAPI, Docker, Docker Compose, GitHub Actions, and DockerHub.

---

# Overview

The ROS2 Monitoring System simulates a simple robotics platform where ROS2 nodes communicate through topics and services, while a web-based dashboard provides real-time visibility into system health and data flow.

This project serves as a practical learning platform for:

* ROS2 Development
* FastAPI Backend Development
* WebSocket Communication
* Docker Containerization
* Continuous Integration (CI)
* Container Registry Management
* Future Kubernetes & GitOps Deployments

---

# Architecture

```text
                     Browser
                        │
                        │ HTTP / WebSocket
                        ▼
              ┌─────────────────┐
              │     FastAPI     │
              │ Backend Bridge  │
              └────────┬────────┘
                       │
                       │ ROS2
                       ▼

         ┌───────────────────────────┐
         │      ROS2 Middleware      │
         └───────────────────────────┘

                 Topic: /counter

          ┌────────────────────┐
          │ Publisher Node     │
          │ (C++)              │
          └─────────┬──────────┘
                    │
                    ▼

              0,1,2,3,4...

                    │
                    ▼

          ┌────────────────────┐
          │ Subscriber Node    │
          │ (C++)              │
          └────────────────────┘

                    ▲
                    │
                    │
          Service: /reset_counter
                    │
                    ▼

              FastAPI /reset
```

---

# Features

## Publisher Node

* Written in C++
* Publishes incrementing integers
* Topic: `/counter`
* Publishing Rate: 1 Hz

Example:

```text
0
1
2
3
4
5
...
```

---

## Subscriber Node

* Written in C++
* Subscribes to `/counter`
* Receives latest publisher value

Example:

```text
Received: 25
Received: 26
Received: 27
```

---

## Reset Service

ROS2 Service:

```text
/reset_counter
```

Allows resetting the publisher counter back to zero.

---

## FastAPI Backend

Provides:

### Health Endpoint

```http
GET /health
```

Returns:

```json
{
  "publisher": true,
  "subscriber": true,
  "system": true
}
```

### Reset Endpoint

```http
POST /reset
```

Triggers ROS2 reset service.

### WebSocket Endpoint

```http
/ws
```

Streams live publisher/subscriber updates to the dashboard.

---

## Frontend Dashboard

Displays:

* System Health Status
* Publisher Counter Value
* Subscriber Counter Value
* Reset Counter Button

Example:

```text
----------------------------------
 ROS2 Nodes Tracking System
----------------------------------

 🟢 Healthy

 Publisher Node

 123

 Subscriber Node

 123

 [ Reset Counter ]
----------------------------------
```

---

# Technology Stack

| Layer            | Technology            |
| ---------------- | --------------------- |
| Frontend         | HTML, CSS, JavaScript |
| Backend          | FastAPI               |
| Middleware       | ROS2 Humble           |
| Languages        | C++, Python           |
| Containerization | Docker                |
| Local Deployment | Docker Compose        |
| CI Platform      | GitHub Actions        |
| Registry         | DockerHub             |
| Testing          | Pytest                |
| Linting          | Ruff                  |
| Security         | Bandit                |

---

# Repository Structure

```text
ros2-monitoring-system/

├── ros2_ws/
│   └── src/
│       └── counter_system/
│
├── backend/
│   ├── app.py
│   ├── ros_bridge.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── tests/
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── docker/
│   ├── ros2.Dockerfile
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
├── docker-compose.yml
│
└── .github/
    └── workflows/
        └── ci.yml
```

---

# Prerequisites

Install:

### Git

```bash
git --version
```

### Docker

```bash
docker --version
```

### Docker Compose

```bash
docker compose version
```

Verify Docker is running:

```bash
docker ps
```

---

# Getting Started

## Clone Repository

```bash
git clone <repository-url>

cd ros2-monitoring-system
```

---

## Build All Containers

```bash
docker compose build
```

Expected:

```text
✔ ros2 image built

✔ backend image built

✔ frontend image built
```

---

## Start Application

```bash
docker compose up
```

or run in detached mode:

```bash
docker compose up -d
```

---

## Verify Running Containers

```bash
docker ps
```

Expected:

```text
ros2

backend

frontend
```

---

# Access Application

## Frontend Dashboard

Open browser:

```text
http://localhost:8080
```

---

## FastAPI API

```text
http://localhost:8000
```

---

## FastAPI Swagger Documentation

```text
http://localhost:8000/docs
```

---

# Test Backend APIs

## Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected:

```json
{
  "publisher": true,
  "subscriber": true,
  "system": true
}
```

---

## Reset Endpoint

```bash
curl -X POST http://localhost:8000/reset
```

Expected:

```json
{
  "message": "reset sent"
}
```

---

# View Logs

## All Containers

```bash
docker compose logs -f
```

---

## Backend Only

```bash
docker compose logs -f backend
```

---

## ROS2 Only

```bash
docker compose logs -f ros2
```

---

## Frontend Only

```bash
docker compose logs -f frontend
```

---

# Stop Application

```bash
docker compose down
```

---

# Local Development Commands

## Run Tests

```bash
cd backend

pytest -v
```

---

## Run Linter

```bash
ruff check backend
```

---

## Run Coverage

```bash
coverage run -m pytest

coverage report
```

---

## Security Scan

```bash
bandit -r backend
```

---

# Continuous Integration Pipeline

Every Git push automatically triggers:

```text
Developer Push
      │
      ▼

GitHub Actions

      │
      ├── Checkout Code
      │
      ├── Install Dependencies
      │
      ├── Ruff Lint
      │
      ├── Pytest
      │
      ├── Coverage Validation
      │
      ├── Bandit Scan
      │
      ├── Build ROS2 Image
      │
      ├── Build Backend Image
      │
      ├── Build Frontend Image
      │
      └── Push Images

      ▼

DockerHub
```

---

# DockerHub Artifacts

Generated automatically:

```text
<dockerhub-user>/ros2-monitoring:<git-sha>

<dockerhub-user>/ros2-backend:<git-sha>

<dockerhub-user>/ros2-frontend:<git-sha>
```

Benefits:

* Immutable Releases
* Version Tracking
* Easy Rollbacks
* Reproducible Deployments

---

# Learning Outcomes

By completing this project, you gain hands-on experience with:

* ROS2 Topics
* ROS2 Services
* FastAPI
* WebSockets
* Docker
* Docker Compose
* GitHub Actions
* DockerHub
* Automated Testing
* Security Scanning
* Continuous Integration

---

# Roadmap

## Phase 6

* Kubernetes Deployment
* Helm Charts
* ConfigMaps
* Secrets

## Phase 7

* ArgoCD
* GitOps
* Automatic Synchronization

## Phase 8

* Blue-Green Deployment
* Canary Deployment
* Rollbacks

---

# CI/CD Maturity Journey

```text
Manual Testing
      │
      ▼

Automated Testing
      │
      ▼

Containerization
      │
      ▼

Continuous Integration
      │
      ▼

Container Registry
      │
      ▼

YOU ARE HERE
──────────────────────────
Production-Style CI
──────────────────────────
      │
      ▼

Kubernetes
      │
      ▼

Helm
      │
      ▼

GitOps
      │
      ▼

ArgoCD
      │
      ▼

Progressive Delivery
```
