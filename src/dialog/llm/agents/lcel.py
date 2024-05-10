
from dialog.db import get_session
from dialog.settings import Settings
from dialog_lib.memory import generate_memory_instance
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.runnables import ConfigurableField
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.output_parsers.json import SimpleJsonOutputParser

# Here we define the model that we will be using as a base for our agent
# as well as the model_name and temperature (some of these parameterers
# are exclusive to OpenAI instances).
chat_model = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=Settings().OPENAI_API_KEY,
).configurable_fields(
    model_name=ConfigurableField(
        id="model_name",
        name="GPT Model",
        description="The GPT model to use"
    ),
    temperature=ConfigurableField(
        id="temperature",
        name="Temperature",
        description="The temperature to use"
    )
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            Settings().PROJECT_CONFIG.get("prompt").get("prompt", "What can I help you with today?")
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

def get_memory_instance(session_id):
    return generate_memory_instance(
        session_id=session_id,
        dbsession=next(get_session()),
        database_url=Settings().DATABASE_URL
    )

chain = prompt | chat_model

runnable = RunnableWithMessageHistory(
    chain,
    get_memory_instance,
    input_messages_key='input',
    history_messages_key="chat_history"
)