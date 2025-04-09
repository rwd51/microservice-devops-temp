# Makefile for Docker Compose Development Environment

# Name of the docker-compose file (can be modified if you have a different name)
DOCKER_COMPOSE_FILE = docker-compose.yml

# UI URLs for monitoring services
PROMETHEUS_URL = http://localhost:9090
GRAFANA_URL = http://localhost:3000
KIBANA_URL = http://localhost:5601

# Default target to start the development environment
dev:
	@echo "Starting development environment..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) up --build --remove-orphans

# Target to stop the containers
stop:
	@echo "Stopping development environment..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

# Target to view logs of the containers
logs:
	@echo "Viewing logs of containers..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f

# Target to view Prometheus UI
prometheus-ui:
	@echo "Opening Prometheus UI..."
	@xdg-open $(PROMETHEUS_URL) || open $(PROMETHEUS_URL) || echo "Please open $(PROMETHEUS_URL) in your browser"

# Target to view Grafana UI
grafana-ui:
	@echo "Opening Grafana UI..."
	@xdg-open $(GRAFANA_URL) || open $(GRAFANA_URL) || echo "Please open $(GRAFANA_URL) in your browser"

# Target to view Kibana UI
kibana-ui:
	@echo "Opening Kibana UI..."
	@xdg-open $(KIBANA_URL) || open $(KIBANA_URL) || echo "Please open $(KIBANA_URL) in your browser"

# Target to view logs of specific services
logs-train:
	@echo "Viewing logs of train-service..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f train-service

logs-auth:
	@echo "Viewing logs of auth-service..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f auth-service

logs-elk:
	@echo "Viewing logs of ELK stack..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f elasticsearch logstash kibana