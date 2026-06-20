from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from ..models import Assessment
from ..schemas import AssessmentStatus

class AssessmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_name(self, name: str) -> Optional[Assessment]:
        stmt = select(Assessment).where(Assessment.name == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_id(self, id: str) -> Optional[Assessment]:
        stmt = select(Assessment).where(Assessment.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> List[Assessment]:
        stmt = select(Assessment)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active(self) -> List[Assessment]:
        stmt = select(Assessment).where(Assessment.status == AssessmentStatus.ACTIVE.value)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_closed(self) -> List[Assessment]:
        stmt = select(Assessment).where(Assessment.status == AssessmentStatus.CLOSED.value)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_archived(self) -> List[Assessment]:
        stmt = select(Assessment).where(Assessment.status == AssessmentStatus.ARCHIVED.value)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_period(self, period: str) -> Optional[Assessment]:
        stmt = select(Assessment).where(Assessment.period == period)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_created_by(self, created_by: str) -> Optional[Assessment]:
        stmt = select(Assessment).where(Assessment.created_by == created_by)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def save(self, assessment: Assessment) -> Assessment:
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    async def delete(self, assessment: Assessment) -> Assessment:
        await self.db.delete(assessment)
        await self.db.commit()
        return assessment