from functools import singledispatch
from typing import Dict

from IndustrialAPI.actors_api_lmdp_ltlf.data import ServiceInstance, TargetInstance
from aida.custom_types import MDPDynamics


class Message:

    TYPE: str


class Register(Message):

    TYPE = "register"

    def __init__(self, service_instance: ServiceInstance) -> None:
        self.service_instance = service_instance


class Update(Message):

    TYPE = "update"

    def __init__(self, service_instance: ServiceInstance) -> None:
        self.service_instance = service_instance

class BreakService(Message):
    
    TYPE = "break_service"

    def __init__(self, action: str) -> None:
        self.action = action


class BreakNextService(Message):
    
    TYPE = "break_next_service"

    def __init__(self, action: str) -> None:
        self.action = action



class RegisterTarget(Message):

    TYPE = "register_target"

    def __init__(self, target_instance: TargetInstance) -> None:
        self.target_instance = target_instance


class RequestTargetAction(Message):

    TYPE = "request_target_action"


class ResponseTargetAction(Message):

    TYPE = "response_target_action"

    def __init__(self, action: str) -> None:
        self.action = action


class ExecuteServiceAction(Message):

    TYPE = "execute_target_action"

    def __init__(self, action: str) -> None:
        self.action = action


class ExecutionResult(Message):

    TYPE = "execution_result"

    def __init__(self, new_state: str, transition_function: MDPDynamics) -> None:
        self.new_state = new_state
        self.transition_function = transition_function


class DoMaintenance(Message):

    TYPE = "do_maintenance"


class UpdateProbabilities(Message):
    
    TYPE = "update_probabilities"


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
        case RegisterTarget.TYPE:
            target_instance = TargetInstance.from_json(payload)
            return RegisterTarget(target_instance)
        case RequestTargetAction.TYPE:
            return RequestTargetAction()
        case ResponseTargetAction.TYPE:
            return ResponseTargetAction(payload["action"])
        case ExecuteServiceAction.TYPE:
            return ExecuteServiceAction(payload["action"])
        case ExecutionResult.TYPE:
            return ExecutionResult(payload["state"], payload["transition_function"])
        case DoMaintenance.TYPE:
            return DoMaintenance()
        case BreakService.TYPE:
            return BreakService(payload["action"])
        case BreakNextService.TYPE:
            return BreakNextService(payload["action"])
        case UpdateProbabilities.TYPE:
            return UpdateProbabilities()

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
def register_target_to_json(message: RegisterTarget):
    return dict(
        type=message.TYPE,
        payload=message.target_instance.json
    )


@to_json.register
def request_target_action_to_json(message: RequestTargetAction):
    return dict(
        type=message.TYPE,
        payload={}
    )


@to_json.register
def response_target_action_to_json(message: ResponseTargetAction):
    return dict(
        type=message.TYPE,
        payload=dict(action=message.action)
    )


@to_json.register
def execute_service_action_to_json(message: ExecuteServiceAction):
    return dict(
        type=message.TYPE,
        payload=dict(action=message.action)
    )


@to_json.register
def execute_ack_to_json(message: ExecutionResult):
    return dict(
        type=message.TYPE,
        payload=dict(
            state=message.new_state,
            transition_function=message.transition_function
        )
    )

@to_json.register
def do_maintenance_to_json(message: DoMaintenance):
    return dict(
        type=message.TYPE,
        payload=dict()
    )


@to_json.register
def break_service_to_json(message: BreakService):
    return dict(
        type=message.TYPE,
        payload=dict(action=message.action)
    )

@to_json.register
def break_next_service_to_json(message: BreakNextService):
    return dict(
        type=message.TYPE,
        payload=dict(action=message.action)
    )

@to_json.register
def update_probabilities(message: UpdateProbabilities):
    return dict(
        type=message.TYPE,
        payload=dict()
    )