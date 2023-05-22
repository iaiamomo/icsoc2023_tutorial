#!/usr/bin/env python3
import asyncio
import json
import sys
from asyncio import CancelledError
from functools import singledispatchmethod
from pathlib import Path

import websockets
from websocket import WebSocket
from websockets.exceptions import ConnectionClosedOK

from IndustrialAPI.actors_api_plan.client_wrapper import WebSocketWrapper
from IndustrialAPI.actors_api_plan.data import ServiceInstance
from IndustrialAPI.actors_api_plan.helpers import setup_logger
from IndustrialAPI.actors_api_plan.messages import Register, Message, ExecuteServiceAction, ExecutionResult

class ServiceDevice:
    def __init__(self, spec: Path, host: str = "localhost", port: int = 8765):
        data = json.loads(spec.read_text())
        self.service_instance = ServiceInstance.from_json(data)
        self._current_state = self.service_instance.service_spec.current_state
        self.logger = setup_logger(self.service_instance.service_id)
        self.host = host
        self.port = port

    async def async_main(self):
        self.logger.info(f"Starting service '{self.service_instance.service_id}'...")
        async with websockets.connect(f"ws://{self.host}:{self.port}") as websocket:
            # register
            self.logger.info("Registering to server...")
            register_message = Register(self.service_instance)
            await WebSocketWrapper.send_message(websocket, register_message)
            while True:
                try:
                    self.logger.info("Waiting for messages from the server...")
                    message = await WebSocketWrapper.recv_message(websocket)
                    self.logger.info("Received message from server, handling it...")
                    await self._handle(message, websocket)
                except (KeyboardInterrupt, ConnectionClosedOK, CancelledError):
                    self.logger.info("Close connection")
                    await websocket.close()
                    break
    
    @singledispatchmethod
    async def _handle(self, message: Message, websocket: WebSocket):
        self.logger.error(f"cannot handle messages of type {message.TYPE}")

    @_handle.register
    async def _handle_execute_service_action(self, message: ExecuteServiceAction, websocket: WebSocket):
        self.logger.info(f"Processing message of type '{message.TYPE}'")
        
        action = message.action
        self.logger.info(f"received action '{action}'")
        self.service_instance.updateState({"state": action["state"], "value": action["result"]})   

        message = ExecutionResult(action)
        self.logger.info(f"Sending result to server")
        await WebSocketWrapper.send_message(websocket, message)


def main(spec):
    """Start service."""
    service_device = ServiceDevice(Path(spec))
    loop = asyncio.get_event_loop()
    task = loop.create_task(service_device.async_main())
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        loop.run_until_complete(task)
    finally:
        loop.close()


if __name__ == '__main__':
    spec = sys.argv[1]
    main(Path(spec))
