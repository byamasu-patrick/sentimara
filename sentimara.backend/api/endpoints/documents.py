import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

import schema
from api import crud
from api.deps import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def get_documents(
    document_ids: Optional[List[UUID]] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[schema.Document]:
    """
    Get all documents or documents by their ids
    """
    if document_ids is None:
        # If no ids provided, fetch all documents
        docs = await crud.fetch_documents(db)
    else:
        # If ids are provided, fetch documents by ids
        docs = await crud.fetch_documents(db, ids=document_ids)  # type: ignore

    if len(docs) == 0:  # type: ignore
        raise HTTPException(status_code=404, detail="Document(s) not found")

    return docs  # type: ignore


@router.get("/{document_id}")
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> schema.Document:
    """
    Get all documents
    """
    docs = await crud.fetch_documents(db, id=document_id)  # type: ignore
    if len(docs) == 0:  # type: ignore
        raise HTTPException(status_code=404, detail="Document not found")

    return docs[0]  # type: ignore
