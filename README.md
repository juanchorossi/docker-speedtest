# Dockerized Speedtest with Tinybird Integration

This project contains a Docker setup for running a speed test using `speedtest-cli` and then sending the test results to Tinybird.

## Prerequisites

Before you can run this project, you need the following:
- Docker installed on your system
- A Tinybird API token and the base URL for Tinybird API

## Setup

1. Clone the repository to your local machine.
2. Navigate to the cloned directory.
3. Make sure you have `speedtest.py` and `Dockerfile` along with a `docker-compose.yml` file within your directory.

Your directory should look like this:

/speedtest-docker
|-- Dockerfile 
|-- speedtest.py 
|-- docker-compose.yml 
|-- README.md


## Configuration

### Environment Variables

The application requires two environment variables:
- `TINYBIRD_TOKEN`: Your API token for the Tinybird service.
- `TINYBIRD_BASE_URL`: The base URL to which the speedtest data will be posted.

You need to create an `.env` file in the root directory and define these variables.

Example `.env` file:

TINYBIRD_TOKEN=your_tinybird_api_token_here TINYBIRD_BASE_URL=https://api.us-east.aws.tinybird.co


Make sure to replace `your_tinybird_api_token_here` with your actual Tinybird API token and use the appropriate base URL.

## Running the Application

With Docker Compose, running the application is straightforward.

1. Build the Docker image with Docker Compose:


Make sure to replace `your_tinybird_api_token_here` with your actual Tinybird API token and use the appropriate base URL.

## Running the Application

With Docker Compose, running the application is straightforward.

1. Build the Docker image with Docker Compose:

```
docker build -t speedtest-docker .
```

2. Start the application in detached mode:
docker-compose up -d

Once started, the `speedtest.py` script will execute every minute and send the results to the specified Tinybird endpoint.

