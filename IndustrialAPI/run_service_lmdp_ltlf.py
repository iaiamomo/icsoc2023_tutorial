#!/usr/bin/env python3
import asyncio
import json
import sys
import random
from asyncio import CancelledError
from functools import singledispatchmethod
from pathlib import Path

import websockets
from websocket import WebSocket
from websockets.exceptions import ConnectionClosedOK

from IndustrialAPI.utils.wrappers import initialize_wrapper
from IndustrialAPI.actors_api_lmdp_ltlf.client_wrapper import WebSocketWrapper
from IndustrialAPI.actors_api_lmdp_ltlf.data import ServiceInstance
from IndustrialAPI.actors_api_lmdp_ltlf.helpers import setup_logger
from IndustrialAPI.actors_api_lmdp_ltlf.messages import Register, Message, ExecuteServiceAction, ExecutionResult, DoMaintenance, BreakService, BreakNextService, UpdateProbabilities
from IndustrialAPI.utils import constants

class ServiceDevice:
    def __init__(self, service_instance: ServiceInstance, host: str = "localhost", port: int = 8765):
        self.service_instance = service_instance
        self.logger = setup_logger(self.service_instance.service_id)
        self._current_state = self.service_instance.service_spec.initial_state
        self.wrapper = initialize_wrapper(self.service_instance.service_spec)
        self.host = host
        self.port = port
        self.logger.info(f"Service '{self.service_instance.service_id}' {type(self.wrapper)}")

    @classmethod
    def from_spec(cls, spec_path: Path, **kwargs) -> "ServiceDevice":
        data = json.loads(spec_path.read_text())
        service_instance = ServiceInstance.from_json(data)
        return ServiceDevice(service_instance)

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
        self.logger.info(f"received action '{message.action}'")

        starting_state = self._current_state
        self.logger.info(f"Current state: {starting_state}")
        transitions_from_current_state = self.wrapper.transition_function[starting_state] # Dict[Action, Tuple[Dict[State, Prob], Tuple[Reward, ...]]]

        self.logger.info(f"Transitions from current state: {transitions_from_current_state}")
        self.logger.info(f"Action: {action}")
        if action not in transitions_from_current_state.keys(): # se non mi trovo in uno stato in cui posso fare quell'azione, rimango nello stato corrente
            await WebSocketWrapper.send_message(websocket, ExecutionResult("null", self.wrapper.transition_function))
            return

        next_service_states, reward = transitions_from_current_state[action] # Tuple[Dict[State, Prob], Tuple[Reward, ...]]
        new_state = max(next_service_states, key=next_service_states.get)
        
        #states, probabilities = zip(*next_service_states.items())
        #new_state = random.choices(states, probabilities)[0] 

        print(self.wrapper.current_state)
        print(self.wrapper._service.to_break)
        
        if self.wrapper.current_state == constants.EXECUTING_STATE_NAME and self.wrapper._service.to_break:
            new_state = constants.BROKEN_STATE_NAME
            self.wrapper._service.to_break = False
        
        self._current_state = new_state
        self.wrapper._current_state = new_state
        self.logger.info(f"Previous state='{starting_state}', current state={new_state}")
        
        # update probabilities and costs of the wrapper
        #self.wrapper.update(starting_state, action)

        message = ExecutionResult(new_state, self.wrapper.transition_function)
        self.logger.info(f"Updated transition function: {message.transition_function}")
        self.logger.info(f"Sending result to server")
        await WebSocketWrapper.send_message(websocket, message)

    @_handle.register
    async def _handle_maintenance(self, message: DoMaintenance, websocket: WebSocket):
        self.logger.info(f"Processing message of type '{message.TYPE}'")
        previous_transition_function = self.wrapper.transition_function
        self.wrapper.reset()
        current_transition_function = self.wrapper.transition_function
        self.logger.info(f"Repaired service: previous tf={previous_transition_function}, new tf={current_transition_function}")

    @_handle.register
    async def _handle_break_service(self, message: BreakService, websocket: WebSocket):
        self.logger.info(f"Processing message of type '{message.TYPE}'")
        self.logger.info("Breaking service...")
        self.wrapper._current_state = constants.BROKEN_STATE_NAME
        self._current_state = constants.BROKEN_STATE_NAME
        self.logger.info("Service broken")

    @_handle.register
    async def _handle_next_break_service(self, message: BreakNextService, websocket: WebSocket):
        self.logger.info(f"Processing message of type '{message.TYPE}'")
        self.logger.info("Setting next break service...")
        self.wrapper._service.to_break = True
        self.logger.info("Service set to break")

    @_handle.register
    async def _handle_update_probabilities(self, message: UpdateProbabilities, websocket: WebSocket):
        self.logger.info(f"Processing message of type '{message.TYPE}'")
        self.logger.info("Updating probabilities")
        self.logger.info("Probabilities updated")


def main(spec):
    """Start service."""
    service_device = ServiceDevice.from_spec(Path(spec))
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
