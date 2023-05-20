from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.target_transitions_by_action import TargetTransitionsByAction


T = TypeVar("T", bound="TargetTransitionFunction")


@attr.s(auto_attribs=True)
class TargetTransitionFunction:
    """a mapping from states to a dictionary of transitions by actions"""

    additional_properties: Dict[str, "TargetTransitionsByAction"] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pass

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.target_transitions_by_action import TargetTransitionsByAction

        d = src_dict.copy()
        target_transition_function = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = TargetTransitionsByAction.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        target_transition_function.additional_properties = additional_properties
        return target_transition_function

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "TargetTransitionsByAction":
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: "TargetTransitionsByAction") -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
