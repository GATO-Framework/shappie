# shappie
AI powered discord bot

## Deployment

This application is packaged as a Docker container. You can use Docker Compose to manage the container.

First, you need to install Docker and Docker Compose on your server if you haven't done so already. You can find instructions in the Docker documentation:

- Docker: https://docs.docker.com/get-docker/
- Docker Compose: https://docs.docker.com/compose/install/

Once Docker and Docker Compose are installed, you can use the following commands to manage the application.

### First time deploy
```shell
docker-compose up --build -d
```
This command builds the Docker image for the application (if it hasn't been built already or if the Dockerfile has changed), and starts the application in the background.

### Shutdown
This may take a few seconds
```shell
docker-compose down
```

### Updating the application
When you want to update the application to the latest version, you can use the following commands:

```shell
docker-compose down
docker-compose up --build -d
```

This will stop the current application container, rebuild the Docker image, and start a new container with the latest version of the application.
