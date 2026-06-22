Here's a professional Markdown document you can place in your repository as:

```text
docs/PROJECT_OVERVIEW.md
```

# ROS2 Monitoring System

## Project Overview & CI Architecture

---

# Overview

The ROS2 Monitoring System is a full-stack application designed to demonstrate modern software delivery practices for robotics and distributed systems.

The project combines:

* ROS2 (C++)
* FastAPI (Python)
* HTML/CSS/JavaScript Frontend
* Docker
* Docker Compose
* GitHub Actions
* DockerHub

The primary goal is to provide a realistic platform for learning and implementing Continuous Integration (CI) and later Continuous Delivery (CD) workflows.

---

# System Architecture

```text
                    Browser
                       │
                       │ HTTP / WebSocket
                       ▼
         ┌──────────────────────────────┐
         │          FastAPI             │
         │      Integration Layer       │
         └──────────────┬───────────────┘
                        │
                        │ ROS2
                        ▼

      ┌─────────────────────────────────┐
      │          ROS2 Middleware        │
      └─────────────────────────────────┘

            Topic: /counter

          ┌──────────────┐
          │ Publisher    │
          │ Node         │
          └──────┬───────┘
                 │
                 ▼

             0,1,2,3...

                 │
                 ▼

          ┌──────────────┐
          │ Subscriber   │
          │ Node         │
          └──────────────┘

                 ▲
                 │
                 │
        Service: /reset_counter
                 │
                 │
         FastAPI Reset API
```

---

# Application Components

## 1. Publisher Node (ROS2 C++)

Responsibilities:

* Publishes integer values
* Starts from 0
* Increments every second
* Publishes on `/counter`

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

## 2. Subscriber Node (ROS2 C++)

Responsibilities:

* Subscribes to `/counter`
* Receives published values
* Stores latest received value

Example:

```text
Received: 15
Received: 16
Received: 17
```

---

## 3. Reset Service

ROS2 Service:

```text
/reset_counter
```

Responsibilities:

* Resets publisher counter
* Counter starts again from 0

Example:

```text
0
1
2
3
...
```

---

## 4. FastAPI Backend

Acts as a bridge between:

* Frontend UI
* ROS2 Backend

Responsibilities:

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

---

### Reset Endpoint

```http
POST /reset
```

Triggers:

```text
/reset_counter
```

ROS2 service.

---

### WebSocket Endpoint

```http
/ws
```

Streams live updates:

```json
{
  "publisher": 123,
  "subscriber": 123
}
```

---

## 5. Frontend Dashboard

Provides:

* ROS2 System Health Indicator
* Publisher Counter Display
* Subscriber Counter Display
* Reset Counter Button

Dashboard Example:

```text
---------------------------------------
ROS2 Nodes Tracking System
---------------------------------------

🟢 HEALTHY

Publisher Node

123

Subscriber Node

123

[ RESET COUNTER ]

---------------------------------------
```

---

# Repository Structure

```text
ros2-monitoring-system/

├── ros2_ws/
│
│   └── src/
│
│       └── counter_system/
│
│           ├── package.xml
│           ├── CMakeLists.txt
│           ├── srv/
│           └── src/
│
├── backend/
│
│   ├── app.py
│   ├── ros_bridge.py
│   ├── requirements.txt
│   └── tests/
│
├── frontend/
│
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── docker/
│
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

# Container Architecture

The application is deployed using multiple containers.

```text
┌─────────────────────┐
│     Frontend        │
│       Nginx         │
└──────────┬──────────┘
           │
           ▼

┌─────────────────────┐
│      FastAPI        │
│    Backend API      │
└──────────┬──────────┘
           │
           ▼

┌─────────────────────┐
│        ROS2         │
│ Publisher Node      │
│ Subscriber Node     │
└─────────────────────┘
```

Benefits:

* Separation of concerns
* Independent deployments
* Easier scaling
* Kubernetes-ready architecture

---

# Continuous Integration Pipeline

The project implements an automated CI pipeline using GitHub Actions.

---

## CI Workflow

```text
Developer
    │
    │ git push
    ▼

GitHub Repository
    │
    ▼

GitHub Actions Runner

    │
    ├── Checkout Source Code
    │
    ├── Install Dependencies
    │
    ├── Ruff Linting
    │
    ├── Pytest Execution
    │
    ├── Coverage Validation
    │
    ├── Bandit Security Scan
    │
    ├── Build ROS2 Docker Image
    │
    ├── Build Backend Docker Image
    │
    ├── Build Frontend Docker Image
    │
    └── Push Images to DockerHub

    ▼

DockerHub Registry
```

---

# CI Quality Gates

Every commit must pass the following validations:

| Validation   | Purpose                |
| ------------ | ---------------------- |
| Ruff         | Code quality           |
| Pytest       | Functional correctness |
| Coverage     | Test coverage          |
| Bandit       | Security scanning      |
| Docker Build | Packaging validation   |
| Docker Push  | Artifact publishing    |

If any validation fails:

```text
Merge Blocked
```

---

# DockerHub Artifacts

CI automatically publishes:

```text
ros2-monitoring:<git-sha>

ros2-backend:<git-sha>

ros2-frontend:<git-sha>
```

Benefits:

* Immutable deployments
* Traceability
* Easy rollback
* Reproducibility

---

# Why This Project Matters

Most CI tutorials focus only on a single language or framework.

This project demonstrates:

* Multi-language development
* C++ and Python integration
* ROS2 middleware
* Service-oriented architecture
* WebSocket communication
* Containerization
* Security validation
* Automated testing
* Artifact publishing

These are the same patterns commonly used in:

* Robotics platforms
* Autonomous systems
* Cloud-native applications
* Distributed software systems

---

# Current Maturity Level

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

Security Validation
      │
      ▼

Artifact Publishing
      │
      ▼

YOU ARE HERE
─────────────────────────
Production-Style CI
─────────────────────────
      │
      ▼

Kubernetes Deployment
      │
      ▼

Helm Packaging
      │
      ▼

GitOps
      │
      ▼

ArgoCD
      │
      ▼

Blue-Green Deployment
```

---

# Future Enhancements

Planned next phases:

### Phase 6

* Kubernetes Deployment
* Helm Charts
* Health Checks
* ConfigMaps
* Secrets

### Phase 7

* ArgoCD
* GitOps
* Automated Sync
* Rollbacks

### Phase 8

* Blue-Green Deployment
* Canary Deployment
* Production Release Strategies

---

# Summary

The ROS2 Monitoring System is a production-style learning platform that combines robotics middleware, backend APIs, frontend visualization, containerization, and modern CI practices.

By completing this project, developers gain practical experience with:

* ROS2
* C++
* Python
* FastAPI
* Docker
* GitHub Actions
* DockerHub
* Automated Testing
* Security Scanning
* CI/CD Foundations

This project serves as a strong foundation for progressing into Kubernetes, Helm, GitOps, and advanced deployment strategies.
