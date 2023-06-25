from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import cast

if TYPE_CHECKING:
  from ..models.service_features import ServiceFeatures
  from ..models.service_attributes import ServiceAttributes





T = TypeVar("T", bound="Service")


@attr.s(auto_attribs=True)
class Service:
    """ 
        Attributes:
            id (str):
            attributes (ServiceAttributes):
            features (ServiceFeatures):
     """

    id: str
    attributes: 'ServiceAttributes'
    features: 'ServiceFeatures'
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.service_features import ServiceFeatures
        from ..models.service_attributes import ServiceAttributes
        id = self.id
        attributes = self.attributes.to_dict()

        features = self.features.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "attributes": attributes,
            "features": features,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.service_features import ServiceFeatures
        from ..models.service_attributes import ServiceAttributes
        d = src_dict.copy()
        id = d.pop("id")

        attributes = ServiceAttributes.from_dict(d.pop("attributes"))




        features = ServiceFeatures.from_dict(d.pop("features"))




        service = cls(
            id=id,
            attributes=attributes,
            features=features,
        )

        service.additional_properties = d
        return service

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
