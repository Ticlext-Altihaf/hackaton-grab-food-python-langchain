from dotenv import load_dotenv

load_dotenv()

from typing import List, Any
from fastapi import FastAPI
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.messages import BaseMessage
from langserve import add_routes
from langchain_core.prompts import ChatPromptTemplate, FewShotPromptTemplate
from langchain_core.runnables import RunnableLambda, ConfigurableField
from langsmith import traceable
from langchain_openai import ChatOpenAI

import os

model = ChatOpenAI()

tools_list = []

prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are assistant to help customer choose the food they want to eat and avoid indecisiveness.
    """),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_openai_functions_agent(model, tools_list, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools_list, verbose=True)

# 4. App definition
app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple API server using LangChain's Runnable interfaces",
)


# 5. Adding chain route

# We need to add these input/output schemas because the current AgentExecutor
# is lacking in schemas.

class Input(BaseModel):
    input: str


class Output(BaseModel):
    output: Any


add_routes(
    app,
    agent_executor,
    input_type=Input,
    output_type=Output,

    path="/agent",
)

if __name__ == "__main__":
    import uvicorn

    port = os.getenv("PORT", 8000)
    port = int(port)
    uvicorn.run(app, host="0.0.0.0", port=port)
