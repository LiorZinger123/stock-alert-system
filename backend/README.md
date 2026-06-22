# Backend System Architecture

This document provides a comprehensive technical overview of the backend architecture.

## 1. High-Level Architecture
The system follows an asynchronous, event-driven microservices pattern. This decouples the user-facing API from intensive background processing tasks, ensuring high availability and responsiveness.

## 2. Component Breakdown

### Core Services
* **FastAPI Backend**: The primary API gateway. It maintains bidirectional communication with the **Client** (via WebSockets/REST) and manages **PostgreSQL** and **Redis** for state and caching. It consumes processed data from **RabbitMQ**.
* **RabbitMQ**: The message broker that serves as the central hub for asynchronous task distribution.

### Worker Layer
* **Price Monitor**: Responsible for periodic external API polling (e.g., yFinance). It updates the **Cache** and **DB**, and publishes events to **RabbitMQ**.
* **Email Producer**: Monitors the **DB** for alerts that need to be sent and queues these as tasks in **RabbitMQ**.
* **Email Consumer**: Monitors **RabbitMQ** for email tasks, executes the SMTP dispatch, and updates the task status in the **DB**.

## 3. Communication & Data Flow
* **API ↔ Client**: Standard client-server communication for user requests and real-time updates.
* **MQ → API**: The message broker pushes processed background data back to the API for real-time notification dispatch.
* **MQ ↔ Consumer**: The consumer actively pulls tasks from the queue and provides acknowledgment/status updates back to the broker.
* **API → DB / API → Cache**: The API initiates write operations to maintain system state and performance.
* **Worker → Storage**: Workers perform necessary bulk syncs and state updates directly to the persistence layer.

## 4. Configuration
To run the backend, you must configure your environment variables. 
1. Copy the provided example file: `cp .env.example .env`
2. Open the newly created `.env` file and populate it with your specific service credentials (database URLs, SMTP settings, etc.).

## 5. Technology Stack
* **Framework**: FastAPI
* **Message Broker**: RabbitMQ
* **Databases**: PostgreSQL (Relational Data), Redis (Caching)
* **Worker Pattern**: Background task consumers