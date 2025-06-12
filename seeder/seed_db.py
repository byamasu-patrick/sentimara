from fire import Fire
from schema import Document, DocumentMetadataKeysEnum
from libs.db.session import SessionLocal
from api import crud
from libs.models.db import table_context_dict
from sqlalchemy import text


async def upsert_single_document(key: str, value: str):
    """
        Upserts a single survey table information into the database using its name.
    """
    async with SessionLocal() as db:

        metadata_map = {
            DocumentMetadataKeysEnum.COLLECTION_NAME: value
        }
        doc = Document(table_name=key, metadata_map=metadata_map)

        document = await crud.upsert_document_by_tablename(db, doc)
        print(f"Upserted document. Database ID:\n{document.id}")


async def main_upsert_single_document():
    """
        Script to upsert a single document by URL. metada_map parameter will be empty dict ({})
        This script is useful when trying to use your own PDF files.
    """
    for key, value in table_context_dict.items():
        key_str = str(key)
        value_str = str(value)
        await upsert_single_document(key_str, value_str)


if __name__ == "__main__":
    Fire(main_upsert_single_document)
