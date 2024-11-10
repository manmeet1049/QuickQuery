from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os, json
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from document_pipeline import DocumentProcessor
from bson import ObjectId


# MongoDB connection details
MONGO_URI = os.getenv("MONGO_URI", "")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database(os.getenv("MONGO_DB",""))  

app = FastAPI()
# Collections
index_collection = db.get_collection(os.getenv("INDEX_COLLECTION",""))
doc_collection = db.get_collection(os.getenv("DOCUMENT_COLLECTION",""))


class Index(BaseModel):
    name: str
    settings: Dict[str, Any] = {}
    mappings: Dict[str, Any] = {}


class Document(BaseModel):
    index: str  # Name of the index
    id: Optional[str] = None  # Optional document ID, auto-generated if not provided
    content: Dict[str, Any]  # Document content, can be a dictionary of any fields


@app.post("/indices/", response_model=dict)
async def create_index(index: Index) -> dict:
    index_data = index.dict()

    # Check if the index already exists
    existing_index = await index_collection.find_one({"name": index.name})
    if existing_index:
        raise HTTPException(status_code=400, detail="Index already exists")

    # Insert the new index into the collection
    result = await index_collection.insert_one(index_data)
    if result.inserted_id:
        return {"status": "success", "id": str(result.inserted_id)}
    raise HTTPException(status_code=500, detail="Index could not be created")


@app.get("/indices/", response_model=List[Index])
async def list_indices() -> List[Index]:
    indices = await index_collection.find().to_list(100)
    return indices


@app.post("/documents/", response_model=dict)
async def index_document(document: Document) -> dict:
    # Retrieve the specified index
    index = await index_collection.find_one({"name": document.index})
    if not index:
        raise HTTPException(status_code=404, detail="Index not found")

    # Prepare the document data for insertion
    document_data = document.content

    # If no ID is provided, auto-generate one using ObjectId from MongoDB
    document_id = document.id if document.id else str(ObjectId())

    # Insert the document into the collection
    document_entry = {
        "_id": document_id,
        "index": document.index,
        "index_id": str(index["_id"]),
        "content": document_data,
    }

    result = await doc_collection.insert_one(document_entry)
    if result.inserted_id:
        # Process the document using the DocumentProcessor
        index_mappings = index.get("mappings", {})
        processor = DocumentProcessor()
        reverse_index = processor.build_reverse_index([document_entry], index_mappings)
        print("---reverse index---", reverse_index)

        # Export the reverse index to the storage (currently a local JSON file)
        DocumentProcessor.export_reverse_index_to_json(reverse_index)

        return {"status": "success", "id": document_id, "index": document.index}

    raise HTTPException(status_code=500, detail="Document could not be indexed")


@app.get("/search/", response_model=dict)
async def search_documents(term: str) -> dict:
    reverse_index = DocumentProcessor.load_reverse_index()
    # Find documents containing the search term
    doc_ids = reverse_index.get(term.upper())  # Ensure term is in uppercase for consistency
    if not doc_ids:
        return {"status": "success", "documents": []}

    # Attempt to convert document IDs to ObjectId if possible
    doc_ids_converted = []
    for doc_id in doc_ids:
        try:
            doc_ids_converted.append(ObjectId(doc_id))  # Convert valid IDs
        except Exception:
            continue  # Skip invalid IDs that can't be converted

    # Query the database for documents with the specified ObjectIds
    documents = await doc_collection.find(
        {"_id": {"$in": doc_ids_converted}}
    ).to_list(length=len(doc_ids_converted))

    # Format the document list in a response-safe way
    response_documents = [{"id": str(doc["_id"]), "content": doc["content"]} for doc in documents]

    return {"status": "success", "documents": response_documents}
