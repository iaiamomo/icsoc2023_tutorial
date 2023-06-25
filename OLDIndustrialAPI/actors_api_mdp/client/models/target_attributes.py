from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, cast

import attr

from ..models.device_type import DeviceType

if TYPE_CHECKING:
    from ..models.target_transition_function import TargetTransitionFunction


T = TypeVar("T", bound="TargetAttributes")


@attr.s(auto_attribs=True)
class TargetAttributes:
    """
    Attributes:
        type (DeviceType):
        transitions (TargetTransitionFunction): a mapping from states to a dictionary of transitions by actions
        initial_state (str):
        final_states (List[str]):
    """

    type: DeviceType
    transitions: "TargetTransitionFunction"
    initial_state: str
    final_states: List[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type.value

        transitions = self.transitions.to_dict()

        initial_state = self.initial_state
        final_states = self.final_states

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
                "transitions": transitions,
                "initial_state": initial_state,
                "final_states": final_states,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.target_transition_function import TargetTransitionFunction

        d = src_dict.copy()
        type = DeviceType(d.pop("type"))

        transitions = TargetTransitionFunction.from_dict(d.pop("transitions"))

        initial_state = d.pop("initial_state")

        final_states = cast(List[str], d.pop("final_states"))

        target_attributes = cls(
            type=type,
            transitions=transitions,
            initial_state=initial_state,
            final_states=final_states,
        )

        target_attributes.additional_properties = d
        return target_attributes

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
