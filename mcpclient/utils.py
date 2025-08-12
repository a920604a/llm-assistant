import re


def clean_json_string(s: str) -> str:
    # 移除開頭的 ```json 與結尾的 ```
    s = s.strip()
    s = re.sub(r"^```json\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s