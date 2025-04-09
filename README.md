Hi.
Run `make dev` to start the development server.

### Pre-commit hooks
pre-commit is in the requirements.txt file in the train-service. Install the requirements with `pip install -r requirements.txt` and run `pre-commit install` to set up the hooks.

### Prmometheus Server:

`http://localhost:9090`

### Grafana Server:

`http://localhost:3000`

### Kibana Server:

1. Go to `http://localhost:5601`

2. Go to "`Stack Management`" (gear icon) in the left menu
3. Select "`Index Patterns`" under Kibana section
4. Click "`Create index pattern`"
   - Create three index patterns named "`microservices-logs-*`", "`train-service-logs-*`", and "`auth-service-logs-*`"
   - Choose "`@timestamp`" as the Time field
5. Go to "`Discover`" in the left menu (under Analytics)

6. Select the required index (train / auth service) pattern

7. Expand the time range in the upper right corner (try "Last 24 hours")
