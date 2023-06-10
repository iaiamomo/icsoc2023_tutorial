from functools import singledispatch
from typing import Dict

from IndustrialAPI.actors_api_plan.data import ServiceInstance

class Message:
    TYPE: str   # variable

class Register(Message):
    TYPE = "register"
    def __init__(self, service_instance: ServiceInstance) -> None:
        self.service_instance = service_instance

class Update(Message):
    TYPE = "update"
    def __init__(self, service_instance: ServiceInstance) -> None:
        self.service_instance = service_instance

class ExecuteServiceAction(Message):
    TYPE = "execute_service_action"
    def __init__(self, serviceAction: Dict) -> None:
        self.action = serviceAction

class ExecutionResult(Message):
    TYPE = "execution_result"
    def __init__(self, update: Dict) -> None:
        self.update = update



def from_json(obj: Dict) -> Message:

    message_type = obj["type"]
    payload = obj["payload"]

    match message_type:
        case Register.TYPE:
            service_instance = ServiceInstance.from_json(payload)
            return Register(service_instance)
        case Update.TYPE:
            service_instance = ServiceInstance.from_json(payload)
            return Update(service_instance)
        case ExecuteServiceAction.TYPE:
            return ExecuteServiceAction(payload["action"])
        case ExecutionResult.TYPE:
            return ExecutionResult(payload["update"])

    raise ValueError(f"message type {message_type} not expected")


@singledispatch
def to_json(message: Message):
    raise NotImplementedError


@to_json.register
def register_to_json(message: Register):
    return dict(
        type=message.TYPE,
        payload=message.service_instance.json
    )


@to_json.register
def update_to_json(message: Update):
    return dict(
        type=message.TYPE,
        payload=message.service_instance.json
    )


@to_json.register
def execute_service_action_to_json(message: ExecuteServiceAction):
    return dict(
        type=message.TYPE,
        payload=dict(action=message.action, )
    )


@to_json.register
def execute_ack_to_json(message: ExecutionResult):
    return dict(
        type=message.TYPE,
        payload=dict(
            update=message.update
        )
    )


