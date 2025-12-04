from typing import Annotated

from pydantic import BaseModel, Field


class EquipmentBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50, examples=["Barbell"])]
    description: Annotated[str | None, Field(max_length=200, default=None)]
    enabled: Annotated[bool, Field(default=True)]


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    enabled: bool | None = None


class EquipmentRead(EquipmentBase):
    id: int
