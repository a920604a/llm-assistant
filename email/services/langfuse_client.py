import os
from contextlib import contextmanager


class LangfuseObs:
    def __init__(self, mode: str = "sdk", environment: str = "development"):
        """
        Wrapper for Langfuse observability
        :param mode: "sdk" (Python SDK), "callback" (LangChain CallbackHandler)
        :param environment: tracing environment (e.g., dev, staging, production)
        """
        self.mode = mode
        self.environment = environment

        os.environ["LANGFUSE_TRACING_ENVIRONMENT"] = environment

        if self.mode == "sdk":
            from langfuse import get_client, observe

            self.langfuse = get_client()
            self.observe = observe
            self.handler = None

        elif self.mode == "callback":
            from langfuse.langchain import CallbackHandler

            self.handler = CallbackHandler()
            self.langfuse = None
            self.observe = None
        else:
            raise ValueError("mode must be 'sdk' or 'callback'")

    # -------------------------------
    # For LangChain
    # -------------------------------
    def get_callbacks(self):
        """給 LangChain chain.invoke 使用"""
        if self.mode == "callback":
            return [self.handler]
        return []

    def get_config(self, user_id: str, tags: list[str] = None, metadata: dict = None):
        """產生 LangChain chain.invoke 的 config"""
        meta = {"langfuse_user_id": user_id}

        if tags:
            meta["langfuse_tags"] = tags

        config = {"metadata": meta}

        if self.mode == "callback":
            config["callbacks"] = [self.handler]

        return config

    # -------------------------------
    # For Python SDK
    # -------------------------------
    def set_user(self, user_id: str):
        if self.mode == "sdk" and self.langfuse:
            self.langfuse.update_current_trace(user_id=user_id)

    def set_tags(self, tags: list[str]):
        if self.mode == "sdk" and self.langfuse:
            self.langfuse.update_current_trace(tags=tags)

    def set_metadata(self, metadata: dict):
        if self.mode == "sdk" and self.langfuse:
            self.langfuse.update_current_trace(metadata=metadata)

    def set_span_metadata(self, metadata: dict):
        if self.mode == "sdk" and self.langfuse:
            self.langfuse.update_current_span(metadata=metadata)

    @contextmanager
    def start_span(self, name: str):
        """Context manager for spans"""
        if self.mode == "sdk" and self.langfuse:
            with self.langfuse.start_as_current_span(name=name) as span:
                yield span
        else:
            yield None

    # -------------------------------
    # Decorator 支援
    # -------------------------------
    def observe_fn(self, fn):
        """Python SDK 模式才需要 decorator"""
        if self.mode == "sdk" and self.observe:
            return self.observe()(fn)
        return fn
