from fastcrud import FastCRUD

from ..models.equipment import Equipment
from ..schemas.equipment import EquipmentCreate, EquipmentRead, EquipmentUpdate

CRUDEquipment = FastCRUD[Equipment, EquipmentCreate, EquipmentUpdate, EquipmentUpdate, dict, EquipmentRead]
crud_equipment = CRUDEquipment(Equipment)
