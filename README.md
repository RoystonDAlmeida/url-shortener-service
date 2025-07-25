# URL Shortener API

A simple, in-memory URL shortener service built with Flask. This application provides API endpoints to create short URLs, redirect users, and view usage statistics. It is designed to be lightweight and thread-safe for concurrent use.

## Table of Contents

- [URL Shortener API](#url-shortener-api)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [API Endpoints](#api-endpoints)
    - [Health Checks](#health-checks)
    - [Core Functionality](#core-functionality)
    - [Debugging](#debugging)
  - [Setup and Installation](#setup-and-installation)
  - [Running Tests](#running-tests)
  - [Design and Technical Details](#design-and-technical-details)

## Features

-   **Shorten URLs**: Convert any long, valid URL into a compact 6-character code.
-   **Redirection**: Automatically redirects from the short URL to the original long URL.
-   **Click Tracking**: Counts the number of times each short URL is accessed.
-   **Usage Statistics**: Provides an endpoint to view the original URL, creation date, and total clicks for any short code.
-   **Thread-Safe**: Uses a `threading.Lock` to safely handle concurrent requests, preventing data corruption and race conditions.
-   **Health Checks**: Includes endpoints for basic service and API health monitoring.

## API Endpoints

The base URL is `http://127.0.0.1:5000`.

### Health Checks

-   **`GET /`**
    -   **Description**: A simple health check for the service.
    -   **Success Response (200)**:
  
        ```json
        {
          "status": "healthy",
          "service": "URL Shortener API"
        }
        ```

-   **`GET /api/health`**
    -   **Description**: An API-specific health check for monitoring.
    -   **Success Response (200)**:
  
        ```json
        {
          "status": "ok",
          "message": "URL Shortener API is running"
        }
        ```

### Core Functionality

-   **`POST /api/shorten`**
    -   **Description**: Creates a new short URL for a given long URL.
    -   **Request Body**:
  
        ```json
        {
          "url": "https://www.example.com"
        }
        ```

    -   **Success Response (200)**:
  
        ```json
        {
          "short_code": "aB1cD2",
          "short_url": "http://127.0.0.1:5000/aB1cD2"
        }
        ```

    -   **Error Responses**:
        -   `400 Bad Request`: If the `url` parameter is missing, empty, or invalid.

            ```json
            {
               "error": "error": "'url' parameter is required in request body"
            }
            ```

        -   `415 Unsupported Media Type`: If the `Content-Type` is not `application/json`.
   
            ```json
            {
               "error": "Content-Type must be application/json"
            }
            ```

        -   `500 Internal Server Error`: If a unique short code cannot be generated after several attempts.

            ```json
            {
               "error": "Could not generate unique code"
            }
           ```

-   **`GET /<short_code>`**
    -   **Description**: Redirects to the original long URL.
    -   **Example**: `GET /aB1cD2`
    -   **Success Response (302 Found)**: Redirects to the long URL.
    -   **Error Response (404 Not Found)**: 
  
         ```json
         {
          "error": "Short code not found"
         }
         ```
        
-   **`GET /api/stats/<short_code>`**
    -   **Description**: Retrieves usage statistics for a short URL.
    -   **Example**: `GET /api/stats/aB1cD2`
    -   **Success Response (200)**:
  
        ```json
        {
          "url": "https://www.example.com",
          "clicks": 5,
          "created_at": "2025-07-25T10:30:00"
        }
        ```

    -   **Error Response (404 Not Found)**: 
  
        ```json
        {
          "error": "Short code not found"
        }
       ```

### Debugging

-   **`GET /api/debug/mappings`**
    -   **Description**: Returns the entire in-memory store of URL mappings. Useful for debugging.
    -   **Success Response (200)**: A JSON object representing the `url_store`.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:RoystonDAlmeida/url-shortener-service.git
    cd url-shortener-service/
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python -m flask --app app.main run
    ```

    The server will start on `http://127.0.0.1:5000`.

## Running Tests

To ensure the application is working correctly, run the test suite using `pytest`.

```bash
pytest
```

The tests cover:
-   Health checks.
-   Successful URL shortening and redirection.
-   Handling of invalid and missing URLs.
-   Correct 404 errors for unknown codes.
-   Statistics tracking.
-   Thread safety under concurrent load.

## Design and Technical Details

-   **In-Memory Storage**: This application uses a simple Python dictionary (`url_store`) as its database. This means all data is **volatile** and will be lost when the application restarts.

-   **Thread Safety**: All read/write operations on the shared `url_store` dictionary are protected by a `threading.Lock` (`store_lock`). This prevents race conditions where multiple concurrent requests could corrupt the data (e.g., two requests trying to write the same short code or update the same click counter simultaneously).

-   **Collision Handling**: The `generate_short_code` function creates a random 6-character code. While collisions are rare, the `shorten_url` endpoint handles them by attempting to generate a new unique code up to 10 times before failing.