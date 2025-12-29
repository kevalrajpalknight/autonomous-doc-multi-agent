# Autonomous Codebase Documenter

This project is a full-stack application that uses an AI agent to autonomously generate documentation for a given GitHub repository. It features a React-based frontend and a Python backend powered by LangGraph, with a focus on real-time user engagement through WebSockets and efficient parallel processing.

## Core Architecture

The application is designed with a clear separation of concerns between the frontend, backend, and the AI agent core.

1.  **Frontend**: A modern Vite + React single-page application provides the user interface. Users can submit a GitHub repository URL and watch the documentation process unfold in real-time. A WebSocket connection streams live logs and status updates, creating an engaging and interactive experience.

2.  **Backend**: A Python-based backend built with FastAPI serves as the main hub. It manages a Celery task queue with a Redis broker to handle long-running documentation jobs. This architecture allows for parallel processing of repository files, significantly reducing the time required to generate documentation.

3.  **AI Core**: The heart of the project is an "AI Agent" built with LangGraph. The agents performs the following steps:

    - Clones the target GitHub repository.
    - Recursively analyzes the file structure.
    - Dispatches file analysis tasks to the Celery queue for parallel execution.
    - Synthesizes the results to generate a complete set of Markdown documentation, including per-folder `README.md` files, function-level explanations, and a "how to run" guide.

4.  **Data & Infrastructure**: Generated documentation is stored, and a link is provided to the user. The combination of Celery and Redis ensures that the system is scalable and can handle multiple documentation requests concurrently.

## How It Works: A High-Level Flow

<img src ="./docs/_Autonomous Codebase Documenter.png" src="simple visual representation of LangGraph workflow">

---

1.  **Submission**: A user pastes a GitHub URL into the React frontend.

2.  **Job Creation**: The frontend sends the URL to the backend via a WebSocket, which initiates a new documentation job.

3.  **Parallel Processing**: The AI agent clones the repo and adds file analysis tasks to the Celery queue. Multiple workers pick up these tasks and process files in parallel.

4.  **Real-time Feedback**: Throughout this process, the agent and workers stream logs and progress updates back to the frontend over the WebSocket. The UI displays these updates in a live terminal.

5.  **Completion**: Once all analysis is complete, the agent assembles the final documentation and sends it to the frontend. The user can then view and copy the generated Markdown.

## Tech Stack

| Area          | Technology                | Purpose                                            |
| :------------ | :------------------------ | :------------------------------------------------- |
| **Backend**   | Python, FastAPI           | API endpoints and WebSocket management             |
| **AI Core**   | LangGraph                 | Orchestrating the autonomous documentation agent   |
| **Queue**     | Celery, Redis             | Parallel processing and handling long-running jobs |
| **Frontend**  | React, Vite, Tailwind CSS | Modern, responsive user interface                  |
| **Real-time** | WebSockets                | Live communication between frontend and backend    |
| **Data**      | S3 / Local Storage        | Storing generated documentation                    |

This combination of technologies creates a powerful, efficient, and user-friendly tool for automated code documentation.
