from prometheus_fastapi_instrumentator import Instrumentator

def setup_metrics(app):
    instrumentator = Instrumentator().instrument(app)
    instrumentator.expose(app, include_in_schema=False)