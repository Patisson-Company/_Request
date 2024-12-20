import typing as _t
from datetime import datetime

from pydantic import BaseModel


class GraphQLBaseModel(BaseModel):
    """
    Base Model for GraphQL object
    """

    class Config:
        allow_population_by_name = True
        json_encoders = {
            # custom output conversion for datetime
            datetime: lambda dt: dt.isoformat()
        }
        arbitrary_types_allowed = True

    def __getattribute__(self, name: str):
        value = super().__getattribute__(name)
        if isinstance(value, EmptyField):
            raise AttributeError(f"The field '{name}' has not been initialized.")
        return value


class EmptyField:
    """
    An empty field for attributes that were not requested in the graphql query
    """
    def __repr__(self) -> _t.Literal['< __EmptyField__ >']:
        return "< __EmptyField__ >"

    @staticmethod
    def empty_field_encoder(obj: object) -> object:
        if isinstance(obj, EmptyField):
            return str(obj.__repr__)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
