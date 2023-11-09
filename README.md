# dialog
Humanized Conversation API (Dialogue)

## Requirements

 - On startup of the application, load the CSV with the knowledge base
 and create an embedding for each row, if embedding already exists, check
 if content has changed and update it if needed.

### Endpoints

 - Initiate a new session
    - POST
 - Chat on session
    - GET
    - POST

## Stack
 - FastAPI
 - Postgres and PGVector
 - Python
 - Langchain