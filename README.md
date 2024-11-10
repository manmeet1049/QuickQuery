# Document Indexing and Search API

This is a FastAPI-based API for managing document indexing and retrieval. Users can create custom indices, add documents to these indices, and perform search operations. The MongoDB database is used to store documents and indices, while an in-memory reverse index optimizes search functionality.

## Table of Contents
- Overview
- Tech Stack
- Installation
- API Endpoints
  - Create Index
  - List Indices
  - Add Document to Index
  - Search Documents
- Usage

## Overview
This API enables the creation, storage, and retrieval of documents in user-defined indices. Each document's content can be indexed for efficient search using a reverse index. This setup allows for fast term-based search operations.

## Tech Stack
- **FastAPI** - Python web framework for building APIs
- **MongoDB** - NoSQL database for storing documents and indices
- **Motor** - Async MongoDB driver for Python
- **Pydantic** - Data validation and settings management using Python type annotations
- **DocumentProcessor** - Custom module for processing documents and creating a reverse index

## Installation
1. Clone the Repository:
   `git clone <repository-url>`
   `cd <repository-directory>`

2. Create and Activate a Virtual Environment:
   `python3 -m venv env`
   `source env/bin/activate`

3. Install Dependencies:
   `pip install -r requirements.txt`

4. Run the FastAPI Server:
   `uvicorn main:app --reload`


## API Endpoints
### 1. Create Index
**Endpoint**: `POST /indices/`  
**Description**: Creates a new index with customizable settings and mappings.

#### Request Body
```json
{
  "name": "index_name",
  "mappings": { "field_name": "data_type" }
}

```

### 2.  List Indices
**Endpoint**: `GET /indices/`
**Description**: Lists all created indices.

### 3. Add Document to Index
**Endpoint**: `POST /documents/`
**Description**: Adds a document to the specified index. If no id is provided, an ID is auto-generated.
#### Request Body
```json
{
  "index": "index_name",
  "content": {
    "field_1": "value_1",
    "field_2": "value_2"
  }
}
```

### 4. Search Documents
**Endpoint**: 'GET /search/'
**Description**: Searches for documents that contain the specified term.

## Query Parameters
**term** - The term to search for in documents.
#### Request Body
```json
{
  "status": "success",
  "documents": [
    {
      "_id": "document_id",
      "index": "index_name",
      "content": { "field_1": "value_1", "field_2": "value_2" }
    }
  ]
}
```

## Usage
### Example cURL Commands

**Create an Index:**
```bash
curl -X POST "http://127.0.0.1:8000/indices/" \
-H "Content-Type: application/json" \
-d '{
      "name": "my_index",
      "settings": { "custom_settings": "example" },
      "mappings": { "title": "text", "description": "text" }
    }'
```
**List Indices:**
```bash
curl -X GET "http://127.0.0.1:8000/indices/"
```
**Add Document to Index:**
```bash
curl -X POST "http://127.0.0.1:8000/documents/" \
-H "Content-Type: application/json" \
-d '{
      "index": "my_index",
      "content": { "title": "Document Title", "description": "Some content here" }
    }'

```
**Search Documents:**
```bash
curl -X GET "http://127.0.0.1:8000/search/?term=example"
```

