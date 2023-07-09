# shappie
AI powered discord bot

## Deployment

> **NOTE:** In order to run Shappie, you'll need the appropriate environment variables.
> These must go in a file called `.env.prod` in the same directory as the `docker-compose.yml`

This application is packaged as a Docker container. You can use Docker Compose to manage the container.

First, you need to install Docker and Docker Compose on your server if you haven't done so already. You can find instructions in the Docker documentation:

- Docker: https://docs.docker.com/get-docker/
- Docker Compose: https://docs.docker.com/compose/install/

Once Docker and Docker Compose are installed, you can use the following commands to manage the application.

### First time deploy
```shell
docker-compose -f docker-compose.yml up --build -d
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
docker-compose -f docker-compose.yml up --build -d
```

This will stop the current application container, rebuild the Docker image, and start a new container with the latest version of the application.


## Development

### Recreate the Database
```shell
docker-compose stop db
docker-compose rm db
docker volume rm shappie_shappie-db
docker-compose up --build -d db
docker-compose logs db
```

## Architecture

### Tools

Tool functions should return a dictionary with various options:
- `use_llm`: This tells the bot to use the LLM to respond to the message, this requires `context`.
- `context`: Additional context passed to the LLM when responding after a using a tool.
- `conent`: The content of the message if not using an LLM. This is added by the LLM if `use_llm` is `True`.
- `image_url`: Creates an embed using the given image URL. Used for GIFs currently.
- `url`: Creates an embed with the given URL. Used for `when2meet` right now.

### Updates
July 7th
- Added vectorstore, webscraper, pdf and text loaders along with vectorstore retriever.
- Added install files for easier setup.
- Minor refactoring when my ocd got to me.
- Filled out the init files so packages should be functioning normally now.
-updated .env to example.env

July 8th
- linked up the vector data base and provided it as a tool. just data consumption to test it out.
- added socratic bot prompt. if it works ill add the works of Socrates to the vectordb
- planning to add the seed and data infromation to the vector database as well.