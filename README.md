# JMF-OpenAI-LLM-Integration

The **JMF-OpenAI-LLM-Integration** is a Python FastAPI application that connects the OpenAI Language Model with the JMF Survey App. Authenticated users can use natural language queries to extract insights from our survey data stored in a PostgreSQL database. TODO: Update to reflect expanded use cases for Modell Mind.

## Features

- **Token-Based Authentication:** Secure access via JWT.
- **Natural Language Processing:** Leverage OpenAI’s GPT model for query processing.
- **Data Retrieval:** Access survey data from PostgreSQL using PgVector.
- **RESTful API:** Built with FastAPI.
- **CORS Enabled:** Cross-Origin support.
- **Containerized:** Docker-ready deployment.

## Technologies

- Python
- FastAPI
- LlamaIndex
- OpenAI GPT Model
- PostgreSQL with PgVector
- JWT for Authentication
- Docker

## Installation & Setup

1. Clone this repository.

2. Navigate to the project directory

3. Install `poetry`:

   ```
   pip install poetry (pip3 install poetry)
   ```

4. Run :

   ```
   poetry shell
   ```

5. Run :

   ```
   poetry install
   ```

6. Update the db url in `the alembic.ini` file:

```
sqlalchemy.url = postgresql://postgres:LuaAhINHCCcM48PXNDa7@localhost:5432/jmf_llm_ai

```

7. Run migrations:

```
alembic upgrade head
```

8. Create a `.env` file in the project directory and set the required environment variables:

   ```
   OPENAI_API_KEY=<Your_OpenAI_API_Key>
   OPENAI_API_KEY=<Your_OpenAI_API_Key>
   POSTGRES_USER=<local postgres user>
   POSTGRES_PASSWORD=<password>
   POSTGRES_DB=<db name>
   POSTGRES_HOST_NAME=localhost
   APP_NAME=JMF-OpenAI-LLM-Integration
   ALLOWED_APP=https://survey.info4pi.org
   DATABASE_HOST_DEV=<Database_Host>
   DATABASE_NAME_DEV=<Database_Name>
   DATABASE_PASSWORD_DEV=<Database_Password>
   DATABASE_PORT_DEV=<Database_Port>
   DATABASE_USERNAME_DEV=<Database_Username>
   SURVEY_AUTHENTICATION_KEY=<Survey_Auth_Key>
   SECRET_KEY=<Secret_Key>

   ```

9. Run the application:

```
uvicorn app:app --reload
```

## API Endpoints

1. `/api/conversation` - POST

   - Create a new conversation
   - Request Payload:

```json
{
  "document_ids": ["string"]
}
```

- Response:

```
{
 "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
 "created_at": "2023-10-16T21:11:50.899Z",
 "updated_at": "2023-10-16T21:11:50.899Z",
 "messages": [
   {
     "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
     "created_at": "2023-10-16T21:11:50.899Z",
     "updated_at": "2023-10-16T21:11:50.899Z",
     "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
     "content": "string",
     "role": "user",
     "status": "PENDING",
     "sub_processes": [
       {
         "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
         "created_at": "2023-10-16T21:11:50.899Z",
         "updated_at": "2023-10-16T21:11:50.899Z",
         "message_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
         "source": "chunking",
         "status": "PENDING",
         "metadata_map": {}
       }
     ]
   }
 ],
 "documents": [
   {
     "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
     "created_at": "2023-10-16T21:11:50.899Z",
     "updated_at": "2023-10-16T21:11:50.899Z",
     "table_name": "string",
     "metadata_map": {}
   }
 ]
}
```

2. `/pi/conversation/conversation_id/message` - POST
   - Chat messages
   - Send a message from a user to a conversation, receive a SSE stream of the assistant's response. Each event in the SSE stream is a Message object. As the assistant continues processing the response, the message object's sub_processes list and content string is appended to. While the message is being generated, the status of the message will be PENDING. Once the message is generated, the status will be SUCCESS. If there was an error in processing the message, the final status will be ERROR.
   - Request Payload:
   ```json
   {
     "conversation_id": ["string"],
     "user_message": ["<Message here>"]
   }
   ```
   - Response:
   ```
   {
     "detail": [
       {
         "loc": [
           "string",
           0
         ],
         "msg": "string",
         "type": "string"
       }
     ]
   }
   ```

## Usage

1. Create a conversation by sending a POST request to `/api/conversation` with the valid documents or tables ids.

2. Send a POST request to `/pi/conversation/conversation_id/message` with your natural language query.

3. The server will respond with the insights retrieved from the survey data.

## Contributing

Contributions are welcome. Please feel free to submit issues or pull requests.

## License

This project is open source, under the terms of the [MIT License](https://opensource.org/licenses/MIT).

## Acknowledgements

- [OpenAI](https://openai.com/) for their incredible Language Model.
- Flask for being an amazing and lightweight web framework
