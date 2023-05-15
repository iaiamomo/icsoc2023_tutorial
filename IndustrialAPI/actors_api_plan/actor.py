from typing import Any, Dict, List



class Actor:
    service_id: str
    service_type: str
    service_subtype: str
    current_state: Any
    actions: Dict[str, Any]

    def __init__(self, service_id: str, service_type: str, service_subtype: str, current_state: Any, actions: Dict[str, Any]) -> None:
        self.service_id = service_id
        self.service_type = service_type
        self.service_subtype = service_subtype
        self.current_state = current_state
        self.actions = actions


def build_actor_from_json(data: Dict) -> "Actor":
        """Get the actor from JSON format."""
        service_id = data["id"]
        service_type = data["attributes"]["type"]
        try:
            service_subtype = data["attributes"]["subtype"]
        except:
            service_subtype = ""
        current_state = data["features"]
        if "Service" in service_type:
            actions_dict = data["attributes"]["actions"]
            actions = {}
            for act in actions_dict.keys():
                action_description = actions_dict[act]["properties"]
                action: Action = build_action_from_json(act, action_description)
                actions[act] = action
            
            return Actor(
                service_id,
                service_type,
                service_subtype,
                current_state,
                actions
            )
        else:
            return Actor(
                service_id,
                service_type,
                service_subtype,
                current_state,
                {}
            )



class Action:
    name: str
    type: str
    command: str
    cost: int
    parameters: List[str]
    requirements: Dict[str, List]
    effects: Dict[str, List]

    def __init__(self, name: str, type: str, command: str, cost: int, parameters: List[str], requirements: Dict[str, List], effects: Dict[str, List]) -> None:
        self.name = name
        self.type = type
        self.command = command
        self.cost = cost
        self.parameters = parameters
        self.requirements = requirements
        self.effects = effects


    def get_result_action(self, registry , parameters: List[str]):
        """Check if the action is conform to the action."""
        update = []
        name_param = ""
        for i in range(len(parameters)):
            paramService = registry.get_service(parameters[i])
            serv_type = paramService.service_spec.service_type
            serv_subtype = paramService.service_spec.service_subtype
            for j in range(len(self.parameters)):
                if serv_type in self.parameters[j]:
                    name_param = self.parameters[j].split(" - ")[1]
                    addedEffect = self.effects["added"]
                    for effect in addedEffect:
                        effectTokens = effect.split(":")
                        paramEffect = effectTokens[0].split(".")
                        nameParamEffect = paramEffect[0]
                        if nameParamEffect == name_param:
                            stateParamEffect = paramEffect[1]
                            resultParamEffect = effectTokens[1]
                            update.append({"service_id": parameters[i], "state": stateParamEffect, "result": resultParamEffect})
        for elem in update:
            #remove duplicates from a list
            while update.count(elem) > 1:
                update.remove(elem)
        return update


def build_action_from_json(name, data) -> "Action":
    """Get the action from JSON format."""
    name = name
    type = data["type"]
    command = data["command"]
    cost = data["cost"]
    parameters = data["parameters"]
    requirements = data["requirements"]
    effects = data["effects"]
    
    return Action(
        name,
        type,
        command,
        cost,
        parameters,
        requirements,
        effects
    )
