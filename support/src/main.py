from support.src.router import support
from fastapi import FastAPI
import consul
import os
import uuid
import socket

app = FastAPI(title="Support")

app.include_router(support, tags=["support"])


@app.get("/", tags=["main page"])
async def root():
    return "Main page of the support service"


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    service_name = "support-service"
    service_port = int(os.getenv("MY_PORT", "8080"))

    register_service(service_name, service_port)


def register_service(service_name, port):
    c = consul.Consul(host='consul')
    service_id = f"{service_name}-{str(uuid.uuid4())}"
    address = os.environ.get('CONTAINER_NAME', 'NOT SET')

    c.agent.service.register(
        name=service_name,
        service_id=service_id,
        address=address,
        port=port,
        tags=["urlprefix-/" + service_name],
        check={
            "http": f"http://{address}:{port}/health",
            "interval": "3s",
            "DeregisterCriticalServiceAfter": "3s",
        },
    )
    print(f"Registered {service_name} with ID {service_id} and address {address}")
