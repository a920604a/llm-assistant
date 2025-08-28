import os

from langfuse.langchain import CallbackHandler

os.environ["LANGFUSE_TRACING_ENVIRONMENT"] = "note service"
langfuse_handler = CallbackHandler()
