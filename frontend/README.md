# Frontend Documentation - Stock-Alert-System

This document provides a comprehensive overview of the frontend architecture for the Stock-Alert-System.

## 1. Overview
The frontend serves as the interactive client layer for the system. It is engineered to maintain bidirectional communication with the backend, offering a highly responsive dashboard for market monitoring and real-time notification handling.

## 2. Technical Architecture & Stack
* **Core Framework**: Built using **React 19** and **Vite** for optimized development and production builds.
* **State Management**: Uses **Zustand** for lightweight global state and **TanStack React Query** for efficient server-state management.
* **Styling & UI**: Utilizes **Material UI (MUI)** with Emotion and **Sass** for styling.
* **Forms & Validation**: Implements **React Hook Form** with Zod/resolvers for robust form handling.
* **Communication**: **Axios** is used for RESTful API calls, supplemented by WebSocket integration for real-time updates.
* **Code Quality**: Enforced via **ESLint** (with React Compiler integration) and **Stylelint** (for SCSS).

## 3. Key Features
* **Real-Time Dashboards**: Interactive visualizations for live stock tracking.
* **Alert Management**: Comprehensive interface for defining, editing, and deleting alert triggers.
* **Notification Feed**: A centralized, reactive feed for backend-pushed updates.
* **Form Logic**: Optimized, validated form submissions across the application.

## 4. Development Setup

### Prerequisites
* Ensure **Node.js** is installed on your machine (LTS version recommended).

### Running the Application
Use the following commands to initialize the development environment:
* **Install Dependencies**: `npm install`
* **Start Development Server**: `npm run dev`

## 5. Maintenance & Quality
* **Linting**: Run `npm run lint` to check for code quality issues or `npm run lint:fix` to automatically fix formatting and linting errors.
* **Production Build**: Run `npm run build` to compile the TypeScript code and generate optimized production assets.