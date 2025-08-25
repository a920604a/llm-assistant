import json
import re

from config import MODEL_NAME
from logger import get_logger
from note_workflow.tasks.llm import llm
from prefect import task

logger = get_logger(__name__)


def clean_json_string(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^```json\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s


@task
def generate_metadata(text: str, model: str = MODEL_NAME) -> dict:
    prompt = f"""
Please read the following tutorial notes and analyze the following attributes:

Topic classification (describe in one paragraph)

Suitable level (Beginner, Intermediate, Advanced)

Three keywords

The tutorial content is as follows:
{text}

Please output in JSON format, for example:
{{
  "title": "Big Data Architecture Design",
  "level": "Intermediate",
  "keywords": ["Data Transformation", "Distributed Storage", "Data Lake"]
}}
"""
    try:
        raw = llm(prompt)
        cleaned = clean_json_string(raw)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("⚠️ JSON parse fail: %s", raw)
            return {"title": "", "level": "", "keywords": []}

        return {
            "title": data.get("title") or data.get("topic", ""),
            "level": data.get("level") or data.get("suitable_level", ""),
            "keywords": (
                data["keywords"]
                if isinstance(data.get("keywords"), list)
                else [
                    kw.strip()
                    for kw in str(data.get("keywords", "")).split(",")
                    if kw.strip()
                ]
            ),
        }
    except Exception as e:
        logger.error(f"Metadata generation failed: {e}")
        return {"title": "", "level": "", "keywords": []}


@task
def ollama_generate_metadata(text: str) -> dict:
    prompt = f"""
請閱讀以下教學筆記，並分析出以下屬性：
- 主題分類（以一段文字描述）
- 適合程度（初學者、中階、進階）
- 三個關鍵字

教學內容如下：
{text}
請用 JSON 格式輸出，例如：
{{
  "title": "大數據架構設計",
  "level": "中階",
  "keywords": ["數據轉型", "分散式儲存", "資料湖"]
}}
"""
    raw = llm(prompt)
    try:
        cleaned = clean_json_string(raw)
        return json.loads(cleaned)
    except Exception:
        logger.warning(f"⚠️ 無法解析 metadata JSON，回傳為：{raw}")
        return {"title": "", "level": "", "keywords": []}
