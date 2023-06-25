import dataclasses
from typing import Any, Dict

from IndustrialAPI.actors_api_plan.actor import Actor, Action, build_actor_from_json


@dataclasses.dataclass(eq=True)
class ServiceInstance:
    service_id: str
    service_spec: Actor
    current_state: Dict
    actions: Dict[str, Any]
    attributes: Dict
    features: Dict

    @classmethod
    def from_json(cls, data: Dict) -> "ServiceInstance":
        """Get the actor from JSON format."""
        service_id = data["id"]
        service_spec = build_actor_from_json(data)
        current_state = service_spec.current_state
        actions = service_spec.actions
        attributes = data["attributes"]
        features = data["features"]

        return ServiceInstance(
            service_id,
            service_spec,
            current_state,
            actions,
            attributes,
            features
        )


    @property
    def json(self) -> Dict:
        """Get the service instance in JSON format."""
        result = dict()

        result["id"] = str(self.service_id)
        result["features"] = self.features
        result["attributes"] = self.attributes
        return result

    
    def updateState(self, update):
        state = update["state"]
        value = update["value"]
        if state in self.current_state.keys():
            deleted = {"state": state, "value": self.current_state[state]["properties"]["value"]}
            self.current_state[state]["properties"]["value"] = value
            self.service_spec.current_state[state]["properties"]["value"] = value
            self.features[state]["properties"]["value"] = value
            return deleted
        return None

    
    def getAction(self, command) -> Action:
        for _, param in self.actions.items():
            assert isinstance(param, Action)
            if command == param.command:
                return param
        return None
