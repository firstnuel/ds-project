
# Distributed Network Scanner and Vulnerability Management System (DNSVMS)

The Distributed Network Scanner and Vulnerability Management System (DNSVMS) is designed to automate network scanning and vulnerability analysis using a distributed system architecture. It leverages Nmap for network scanning, integrates AI for advanced analysis of scan results, and provides a user-friendly web interface for system interaction. This system is aimed at  looking to enhance their network security posture through efficient scanning and insightful vulnerability analysis.


This guide will help you set up and run the DNSVMS using Docker Compose. The system consists of three services: `node1-app`, `processor-app`, and `analysis-app`.

## Prerequisites

- Docker installed on your machine. For installation instructions, visit [Docker's official website](https://docs.docker.com/get-docker/).
- Docker Compose installed. It comes bundled with Docker for Windows and Docker for Mac. For Linux, follow the [installation instructions](https://docs.docker.com/compose/install/).

## Project Structure

Ensure your project directory is structured as follows:

```plaintext
/project-directory
    /node1
        Dockerfile
    /node2
        Dockerfile
    /node3
        Dockerfile
    docker-compose.yml
```

## Running the Application

1. **Clone the Repository** (if applicable):
   Clone the project repository to your local machine or ensure you are in the project directory where the `docker-compose.yml` file is located.

  ```shell
   git clone https://github.com/firstnuel/ds-project.git
   cd ds-project
  ```


-  To use this service, you will need an API key from [OPENAI](https://openai.com/). Follow these steps to set up your environment
-  1. Obtain an API key by [link to obtain the API key](https://platform.openai.com/api-keys).
-  2. Create a file named `.env` in the `/node3` directory of this project.
-  3. Inside the `.env` file, add the following line (replace `YOUR_API_KEY_HERE` with the key you obtained):
      ```
      OPENAI_API_KEY=YOUR_API_KEY_HERE
      ```

2. **Build and Run Containers**:
   Open a terminal and navigate to the root of your project directory. Run the following command to build and start your containers:

   ```shell
   docker-compose up --build
   ```

   This command does the following:
   - Builds images for the services defined in docker-compose.yml if they don't exist.
   - Starts the containers specified in the docker-compose.yml file.
   - The `--build` flag ensures that Docker builds the images before starting the containers, which is useful if you have made changes to your Dockerfiles or service configurations.


3. **Accessing the Applications**:
   - `node1-app` will be accessible at `http://localhost:5001`
   - `processor-app` will be accessible at `http://localhost:5002`
   - `analysis-app` will be accessible at `http://localhost:5003`
   
   Replace localhost with the IP address or hostname of your Docker host if you are not running the containers locally.

4. **Initiating a Scan**:
   
   To initiate a network scan, navigate to the node1-app web interface using the address provided above. Input a valid IP address for scanning and follow the on-screen instructions to         start the scanning process. The results will be processed and analyzed through the system's distributed architecture, providing insights into potential vulnerabilities.

## Stopping the Application

To stop and remove the containers, networks, and images created by `docker-compose up`, run the following command in the terminal:

```shell
docker-compose down
```

## Additional Commands

- To view the logs of all running containers, use:
  ```shell
  docker-compose logs
  ```

- To rebuild the images and restart the containers, use:
  ```shell
  docker-compose up --build -d
  ```

- To stop all containers without removing them, use:
  ```shell
  docker-compose stop
  ```

## Troubleshooting

If you encounter any issues with your Docker Compose setup, consult the [Docker Compose documentation](https://docs.docker.com/compose/) or check the specific error message you are receiving for troubleshooting tips.

