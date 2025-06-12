from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from api import crud
from api import deps


router = APIRouter()


@router.get("/")
async def health(db: AsyncSession = Depends(deps.get_db)) -> Dict[str, str]:
    """
    Health check endpoint.
    """

    result = await crud.update_conversation_headline(
        db=db, conversation_id="d468fb21-5fdf-4def-86d8-c2f964bcbc45")

    await db.execute(text("SELECT 1"))
    return {"status": "alive"}
