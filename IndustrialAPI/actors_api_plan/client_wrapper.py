"""Wrapper class to auto-generated OpenAPI client functions."""
import json
from typing import List

from websocket import WebSocket

from IndustrialAPI.actors_api_plan.client import Client
from IndustrialAPI.actors_api_plan.client.api.services.app_server_api_get_services import asyncio_detailed as get_services
from IndustrialAPI.actors_api_plan.client.api.services.app_server_api_execute_service_action import asyncio_detailed as execute_service_action
from IndustrialAPI.actors_api_plan.client.api.services.app_server_api_get_service import asyncio_detailed as get_service
from IndustrialAPI.actors_api_plan.client.api.services.app_server_api_break_service import asyncio_detailed as break_service
from IndustrialAPI.actors_api_plan.client.models import Service

from IndustrialAPI.actors_api_plan.actor import Actor
from IndustrialAPI.actors_api_plan.messages import Message, from_json, to_json

TIMEOUT = 60.0


class ClientWrapper:

    def __init__(self, host: str, port: int, timeout: float = TIMEOUT) -> None:
        """Initialize the client wrapper"""
        self._host = host
        self._port = port
        self._timeout = timeout

        self._client = Client(self.base_url, timeout=timeout, verify_ssl=False)

    @property
    def base_url(self) -> str:
        """Initialize the base URL."""
        return f"http://{self._host}:{self._port}"

    async def get_services(self) -> List[Actor]:
        """Get all the services."""
        response = await get_services(client=self._client)
        result: List[Service] = response.parsed
        to_our_model = [Actor.from_json(service.to_dict()) for service in result]
        return to_our_model

    async def get_service(self, service_id: str) -> Actor:
        """Get all the services."""
        response = await get_service(service_id, client=self._client)
        return Actor.from_json(response.parsed.to_dict())

    async def execute_service_action(self, service_id: str, action: str) -> None:
        """Execute service action."""
        response = await execute_service_action(service_id, json_body=action, client=self._client)
        return response.parsed
    
    async def break_service(self, service_id: str):
        response = await break_service(service_id)
        return response.parsed
        


class WebSocketWrapper:

    @classmethod
    async def send_message(cls, websocket: WebSocket, message: Message):
        json_message = to_json(message)
        raw_message = json.dumps(json_message)
        await websocket.send(raw_message)

    @classmethod
    async def recv_message(cls, websocket: WebSocket) -> Message:
        raw_message = await websocket.recv()
        json_message = json.loads(raw_message)
        return from_json(json_message)
