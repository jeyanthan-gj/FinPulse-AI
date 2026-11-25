import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# Load variables from .env
load_dotenv()


# Create a reusable LLM instance
# stream_chunk_timeout and timeout disabled to prevent premature stream drops on slow proxies
llm = ChatOpenAI(
    model=os.getenv("MODEL"),
    base_url=os.getenv("OPENAI_API_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.2,
    timeout=300,
    stream_chunk_timeout=None,
)
