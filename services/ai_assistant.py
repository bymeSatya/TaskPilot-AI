import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Setup Groq
groq_key = st.secrets["groq_key"]
os.environ["GROQ_API_KEY"] = groq_key

model = ChatGroq(model="openai/gpt-oss-120b")

# Prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI assistant specialized in Snowflake and Matillion. "
                   "Analyze the situation and provide efficient, step-by-step guidance."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ]
)

# Chat with memory
memory_store = {}

def get_chat(session_id="default"):
    if session_id not in memory_store:
        memory_store[session_id] = InMemoryChatMessageHistory()
    return RunnableWithMessageHistory(
        model | prompt,
        lambda: memory_store[session_id],
        input_messages_key="input",
        history_messages_key="history"
    )

def ask_ai(question, session_id="default"):
    chat = get_chat(session_id)
    response = chat.invoke({"input": question})
    return response.content
