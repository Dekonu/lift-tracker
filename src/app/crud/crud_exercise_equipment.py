from fastcrud import FastCRUD
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.exercise_equipment import ExerciseEquipment


class CRUDExerciseEquipment(FastCRUD[ExerciseEquipment, dict, dict, dict, dict, dict]):
    """CRUD operations for exercise-equipment relationships."""
    
    async def get_by_exercise(self, db: AsyncSession, exercise_id: int) -> list[dict]:
        """Get all equipment for an exercise."""
        result = await self.get_multi(db=db, exercise_id=exercise_id)
        return result.get("data", [])
    
    async def get_by_equipment(self, db: AsyncSession, equipment_id: int) -> list[dict]:
        """Get all exercises for an equipment."""
        result = await self.get_multi(db=db, equipment_id=equipment_id)
        return result.get("data", [])
    
    async def link_equipment(self, db: AsyncSession, exercise_id: int, equipment_id: int) -> ExerciseEquipment:
        """Link equipment to an exercise."""
        # Check if link already exists
        existing = await self.get(
            db=db,
            exercise_id=exercise_id,
            equipment_id=equipment_id,
        )
        if existing:
            return existing
        
        # Create new link
        link_data = {
            "exercise_id": exercise_id,
            "equipment_id": equipment_id,
        }
        return await self.create(db=db, object=link_data)
    
    async def unlink_equipment(self, db: AsyncSession, exercise_id: int, equipment_id: int) -> None:
        """Unlink equipment from an exercise."""
        link = await self.get(
            db=db,
            exercise_id=exercise_id,
            equipment_id=equipment_id,
        )
        if link:
            link_id = link.id if hasattr(link, "id") else link["id"]
            await self.db_delete(db=db, id=link_id)
    
    async def set_equipment_for_exercise(self, db: AsyncSession, exercise_id: int, equipment_ids: list[int]) -> None:
        """Set equipment for an exercise (replaces existing links)."""
        # Get current equipment
        current_links = await self.get_by_exercise(db=db, exercise_id=exercise_id)
        current_equipment_ids = {
            link.equipment_id if hasattr(link, "equipment_id") else link["equipment_id"]
            for link in current_links
        }
        
        # Remove equipment not in new list
        for equipment_id in current_equipment_ids:
            if equipment_id not in equipment_ids:
                await self.unlink_equipment(db=db, exercise_id=exercise_id, equipment_id=equipment_id)
        
        # Add new equipment
        for equipment_id in equipment_ids:
            if equipment_id not in current_equipment_ids:
                await self.link_equipment(db=db, exercise_id=exercise_id, equipment_id=equipment_id)


crud_exercise_equipment = CRUDExerciseEquipment(ExerciseEquipment)

