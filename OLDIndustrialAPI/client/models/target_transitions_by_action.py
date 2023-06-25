from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

T = TypeVar("T", bound="TargetTransitionsByAction")


@attr.s(auto_attribs=True)
class TargetTransitionsByAction:
    """a mapping from action to transitions and rewards"""

    additional_properties: Dict[str, List[Union[float, str]]] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = []
            for componentsschemas_target_transition_item_data in prop:
                componentsschemas_target_transition_item: Union[float, str]

                componentsschemas_target_transition_item = componentsschemas_target_transition_item_data

                field_dict[prop_name].append(componentsschemas_target_transition_item)

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        target_transitions_by_action = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = []
            _additional_property = prop_dict
            for componentsschemas_target_transition_item_data in _additional_property:

                def _parse_componentsschemas_target_transition_item(data: object) -> Union[float, str]:
                    return cast(Union[float, str], data)

                componentsschemas_target_transition_item = _parse_componentsschemas_target_transition_item(
                    componentsschemas_target_transition_item_data
                )

                additional_property.append(componentsschemas_target_transition_item)

            additional_properties[prop_name] = additional_property

        target_transitions_by_action.additional_properties = additional_properties
        return target_transitions_by_action

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> List[Union[float, str]]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: List[Union[float, str]]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
