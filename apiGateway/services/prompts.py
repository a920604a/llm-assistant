from api.schemas.SystemSetting import SystemSettings


def build_prompt(
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
