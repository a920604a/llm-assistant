from typing import Dict, List

from api.schemas.SystemSetting import SystemSettings


def build_prompt(query: str, retrieved_chunks: List[Dict]) -> str:
    context = (
        "\n".join([c["chunk_text"] for c in retrieved_chunks[:3]])
        if retrieved_chunks
        else ""
    )
    prompt = f"User question: {query}\nRelevant context:\n{context}\nPlease answer the question based on the above context."
    return prompt


def build_system_prompt(
    query: str, system_setting: SystemSettings, user_id: str = "anonymous"
):
    isTranslate = system_setting.translate
    user_language = system_setting.user_language
    system_prompt = system_setting.system_prompt

    # 建 prompt
    if isTranslate:
        prompt_text = f"""
        {system_prompt}
        You are a helpful assistant.

        Question:
        {query}

        Answer in {user_language}, concise and clear.
        """
    else:
        prompt_text = f"""
        {system_prompt}
        You are a helpful assistant.

        Question:
        {query}

        Answer concise and clear.
        """

    return prompt_text
