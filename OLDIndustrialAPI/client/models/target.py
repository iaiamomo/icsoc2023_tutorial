from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.target_attributes import TargetAttributes


T = TypeVar("T", bound="Target")


@attr.s(auto_attribs=True)
class Target:
    """
    Attributes:
        id (str):
        attributes (TargetAttributes):
    """

    id: str
    attributes: "TargetAttributes"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        attributes = self.attributes.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "attributes": attributes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.target_attributes import TargetAttributes

        d = src_dict.copy()
        id = d.pop("id")

        attributes = TargetAttributes.from_dict(d.pop("attributes"))

        target = cls(
            id=id,
            attributes=attributes,
        )

        target.additional_properties = d
        return target

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
