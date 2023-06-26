from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.transition_function import TransitionFunction


T = TypeVar("T", bound="ServiceFeatures")


@attr.s(auto_attribs=True)
class ServiceFeatures:
    """
    Attributes:
        current_state (str):
        transition_function (TransitionFunction): a mapping from states to a dictionary of transitions by actions
    """

    current_state: str
    transition_function: "TransitionFunction"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        current_state = self.current_state
        transition_function = self.transition_function.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "current_state": current_state,
                "transition_function": transition_function,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.transition_function import TransitionFunction

        d = src_dict.copy()
        current_state = d.pop("current_state")

        transition_function = TransitionFunction.from_dict(d.pop("transition_function"))

        service_features = cls(
            current_state=current_state,
            transition_function=transition_function,
        )

        service_features.additional_properties = d
        return service_features

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
