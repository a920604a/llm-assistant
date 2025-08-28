import os

from langfuse.langchain import CallbackHandler

os.environ["LANGFUSE_TRACING_ENVIRONMENT"] = "email service"
langfuse_handler = CallbackHandler()
