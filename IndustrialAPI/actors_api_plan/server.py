import asyncio
import json
import signal
from asyncio import AbstractEventLoop, CancelledError
from functools import singledispatchmethod
from threading import Thread
from typing import Dict, Optional, List, cast

import websockets
from websocket import WebSocket
from websockets.exceptions import ConnectionClosedOK

from IndustrialAPI.actors_api_plan.client_wrapper import WebSocketWrapper
from IndustrialAPI.actors_api_plan.data import ServiceInstance
from IndustrialAPI.actors_api_plan.actor import Action
from IndustrialAPI.actors_api_plan.helpers import setup_logger
from IndustrialAPI.actors_api_plan.messages import from_json, Message, Register, Update, \
    ExecuteServiceAction, ExecutionResult

#from helpers import normpdf


logger = setup_logger(name="server")


class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, ServiceInstance] = {}
        self.sockets_by_service_id: Dict[str, WebSocket] = {}
        self.service_id_by_sockets: Dict[WebSocket, str] = {}

    def has_service(self, service_id: str) -> bool:
        return service_id in self.services

    def get_services(self) -> List[ServiceInstance]:
        return list(self.services.values())

    def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        return self.services.get(service_id, None)

    def add_service(self, service_instance: ServiceInstance, socket: WebSocket):
        if service_instance.service_id in self.services:
            raise ValueError(f"already registered a service with id {service_instance.service_id}")
        self.services[service_instance.service_id] = service_instance
        self.sockets_by_service_id[service_instance.service_id] = socket
        self.service_id_by_sockets[socket] = service_instance.service_id

    def remove_service(self, service_id: str):
        self.services.pop(service_id)
        socket = self.sockets_by_service_id.pop(service_id)
        self.service_id_by_sockets.pop(socket)

    def update_service(self, service_id: str, service_instance: ServiceInstance) -> None:
        assert self.has_service(service_id)
        self.services[service_id] = service_instance



class WebsocketServer:
    def __init__(self, _registry: ServiceRegistry, port: int, loop: Optional[AbstractEventLoop] = None) -> None:
        """Initialize the websocket server."""
        self.registry = _registry
        self.port = port
        self.loop = loop

        self._loop: Optional[AbstractEventLoop] = None
        self._thread = Thread(target=self.serve_sync)
        self._server_task: Optional[asyncio.Task] = None

        self._websockets = []

    def serve_sync(self):
        """Wrapper to the 'serve' async method."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._server_task = self._loop.create_task(self.serve())
        try:
            self._loop.run_until_complete(self._server_task)
        except asyncio.CancelledError:
            pass

    async def serve(self):
        # run the websocket server with the request_handler
        async with websockets.serve(self.request_handler, "localhost", self.port):
            await asyncio.Future()  # run forever

    async def request_handler(self, websocket):
        try:
            # handle registration
            raw_message = await websocket.recv()
            message_json = json.loads(raw_message)
            message = from_json(message_json)
            assert isinstance(message, (Register)) # register the service
            await self._handle(message, websocket)
            # don't close connection - communcation is handled elsewhere
            while True:
                await asyncio.Future()
        except ConnectionClosedOK:
            logger.info(f"Closed connection with {websocket.remote_address}")
        except CancelledError:
            logger.info(f"Tearing down server")
        except Exception as e:
            logger.error(f"an error occurred: {e}")
        finally:
            await self._unsubscribe(websocket)

    async def _unsubscribe(self, websocket: WebSocket):
        if websocket in self.registry.service_id_by_sockets:
            # service registered, removing it
            service_id = self.registry.service_id_by_sockets[websocket]
            logger.info(f"Service {service_id} disconnected, removing it...")
            self.registry.remove_service(service_id)

    @singledispatchmethod
    async def _handle(self, message: Message, websocket: WebSocket) -> None:
        """Handle the message."""

    @_handle.register
    async def _handle_register(self, register: Register, websocket: WebSocket) -> None:
        """Handle the register message."""
        self.registry.add_service(register.service_instance, websocket)
        logger.info(f"Registered service {register.service_instance.service_id}")

    @_handle.register
    async def _handle_update(self, update: Update, websocket: WebSocket) -> None:
        """Handle the update message."""
        try:
            self.registry.update_service(update.service_instance.service_id, update.service_instance)
            logger.info(f"Updated service {update.service_instance.service_id}")
        except Exception as e:
            logger.error(f"An error occurred while updating the service: {e}")
            await websocket.close()

    def start(self):
        self._thread.start()

    def stop(self):
        self._loop.call_soon_threadsafe(self._server_task.cancel)
        self._thread.join()



class Api:
    SERVICES: Dict[str, ServiceInstance] = {}

    def __init__(self, websocket_server: WebsocketServer):
        self.websocket_server = websocket_server

    @property
    def registry(self) -> ServiceRegistry:
        return self.websocket_server.registry

    def _log_call(self, func_name, kwargs: Optional[Dict] = None):
        kwargs = kwargs if kwargs is not None else {}
        logger.info(f"Called '{func_name}' with args: {kwargs}")

    async def get_services(self):
        self._log_call(self.get_services.__name__)
        return [service.json for service in self.registry.get_services()], 200

    async def get_service(self, service_id: str):
        self._log_call(self.get_service.__name__, dict(service_id=service_id))
        service_id = str(service_id)
        result = self.registry.get_service(service_id)
        if result is None:
            return f'Service with id {service_id} not found', 404
        return result.json, 200

    async def break_service(self, service_id: str):
        self._log_call(self.break_service.__name__, dict(service_id=service_id))
        service_id = str(service_id)
        result = self.registry.get_service(service_id)
        if result is None:
            return f'Service with id {service_id} not found', 404
        result.current_state["status"]["properties"]["value"] = "broken"
        return result.json, 200

    async def execute_service_action(self, service_id: str, body: str):
        self._log_call(self.execute_service_action.__name__, dict(service_id=service_id, body=body))
        actionBody = body
        service_id = str(service_id)
        service = self.registry.get_service(service_id)
        if service is None:
            return f'Service with id {service_id} not found', 404

        #rompi il servizio -> DA TESTARE
        """ 
        prob = normpdf()
        if prob > 0.7:
            service.current_state["status"]["properties"]["value"] = "broken"
            service.features["status"]["properties"]["value"] = "broken"
            service.service_spec.current_state["status"]["properties"]["value"] = "broken"
            return f'Service with id {service_id} is broken', 404
        """

        contain = "status" in service.current_state
        cost = 0
        if contain and service.current_state["status"]["properties"]["value"] == "available":
            command = actionBody["command"]
            service_name = actionBody["service_id"]
            parameters = actionBody["parameters"]
            assert service_name == service_id

            service_instance = self.registry.get_service(service_id)
            action: Action = service_instance.getAction(command)
            actionResult = action.get_result_action(self.registry, parameters)
            if actionResult == {}:
                return f'Error in finding effect of action {command}', 404

            cost = action.cost
            added_param = []
            deleted_param = []
            for actionRes in actionResult:
                # invio modifica dello stato
                serviceToCall = actionRes["service_id"]
                websocket = self.registry.sockets_by_service_id[serviceToCall]
                request = ExecuteServiceAction(actionRes)
                await WebSocketWrapper.send_message(websocket, request)

                # waiting reply from service
                response: ExecutionResult = await WebSocketWrapper.recv_message(websocket)
                assert response.TYPE == ExecutionResult.TYPE
                message = response.update
                #check if status is broken
                if message["state"] == "status" and message["result"] == "broken":
                    added_param = ["broken"]
                    deleted_param = []
                    break
                else:
                    service_id_updated = message["service_id"]
                    state_updated = message["state"]
                    result_updated = message["result"]

                    # update service of server
                    service_instance = self.registry.get_service(service_id_updated)
                    deleted = service_instance.updateState({"state": state_updated, "value": result_updated})
                    state_deleted = deleted["state"]
                    result_deleted = deleted["value"]

                    added_param.append(f"{service_id_updated}.{state_updated}:{result_updated}")
                    deleted_param.append(f"{service_id_updated}.{state_deleted}:{result_deleted}")
        else:
            added_param = [f"{service.service_id}.status:broken"]
            deleted_param = []

        messageToReturn = {
            "value": "terminated",
            "output": {"added": added_param, "deleted": deleted_param},
            "cost": cost
        }

        return messageToReturn, 200



class Server:
    SERVICES: Dict[str, ServiceInstance] = {}

    def __init__(self, http_port: int = 8080, websocket_port: int = 8765, loop: Optional[AbstractEventLoop] = None):
        """Initialize the API service."""
        self._http_port = http_port
        self._websocket_port = websocket_port
        self._loop = loop

        self._registry = ServiceRegistry()
        self._server = WebsocketServer(self._registry, websocket_port, loop=loop)
        self._api = Api(self._server)

        self._original_sigint_handler = signal.getsignal(signal.SIGINT)

    def _sigint_handler(self, signal_, frame):
        self._server.stop()
        self._original_sigint_handler(signal_, frame)

    def _overwrite_sigint_handler(self):
        signal.signal(signal.SIGINT, self._sigint_handler)

    @property
    def api(self) -> Api:
        return self._api

    def run(self, port: int = 8080) -> None:
        from IndustrialAPI.actors_api_plan.app import app
        self._overwrite_sigint_handler()
        task = self._loop.create_task(self._server.serve())
        app.run(port=port, debug=True, loop=self._loop)



server = Server(loop=asyncio.get_event_loop())
