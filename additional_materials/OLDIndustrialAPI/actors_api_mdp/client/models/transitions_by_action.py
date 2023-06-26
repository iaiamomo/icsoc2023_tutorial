from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

if TYPE_CHECKING:
    from ..models.prob_distribution import ProbDistribution


T = TypeVar("T", bound="TransitionsByAction")


@attr.s(auto_attribs=True)
class TransitionsByAction:
    """a mapping from action to transitions and rewards"""

    additional_properties: Dict[str, List[Union["ProbDistribution", float]]] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.prob_distribution import ProbDistribution

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = []
            for componentsschemasreward_and_prob_distribution_item_data in prop:
                componentsschemasreward_and_prob_distribution_item: Union[Dict[str, Any], float]

                if isinstance(componentsschemasreward_and_prob_distribution_item_data, ProbDistribution):
                    componentsschemasreward_and_prob_distribution_item = (
                        componentsschemasreward_and_prob_distribution_item_data.to_dict()
                    )

                else:
                    componentsschemasreward_and_prob_distribution_item = (
                        componentsschemasreward_and_prob_distribution_item_data
                    )

                field_dict[prop_name].append(componentsschemasreward_and_prob_distribution_item)

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.prob_distribution import ProbDistribution

        d = src_dict.copy()
        transitions_by_action = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = []
            _additional_property = prop_dict
            for componentsschemasreward_and_prob_distribution_item_data in _additional_property:

                def _parse_componentsschemasreward_and_prob_distribution_item(
                    data: object,
                ) -> Union["ProbDistribution", float]:
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        componentsschemasreward_and_prob_distribution_item_type_0 = ProbDistribution.from_dict(data)

                        return componentsschemasreward_and_prob_distribution_item_type_0
                    except:  # noqa: E722
                        pass
                    return cast(Union["ProbDistribution", float], data)

                componentsschemasreward_and_prob_distribution_item = (
                    _parse_componentsschemasreward_and_prob_distribution_item(
                        componentsschemasreward_and_prob_distribution_item_data
                    )
                )

                additional_property.append(componentsschemasreward_and_prob_distribution_item)

            additional_properties[prop_name] = additional_property

        transitions_by_action.additional_properties = additional_properties
        return transitions_by_action

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> List[Union["ProbDistribution", float]]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: List[Union["ProbDistribution", float]]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
