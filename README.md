# shappie
AI powered discord bot


## Deployment

### First time deploy
```shell
docker build -t shappie .
docker run --name shappie --env-file .env --rm -d shappie
```

### Shutdown
This may take a few seconds
```shell
docker stop shappie
```
