
from agent.rag_agent import retrieve_docs
from agent.vision_agent import describe_image
from agent.llm_router import ask_llm

async def handle_user_query(text: str = None, image: bytes = None):
    description = ""

    if image:
        description = describe_image(image)  # GPT-4o 或 CLIP 等

    full_prompt = ""
    if text and description:
        full_prompt = f"圖片內容為：{description}\n\n使用者提問：{text}"
    elif text:
        full_prompt = text
    elif description:
        full_prompt = f"請根據以下圖片內容進行回答：{description}"
    else:
        return "請提供文字或圖片作為輸入"

    docs = retrieve_docs(full_prompt)
    response = ask_llm(full_prompt, context=docs)
    return response

