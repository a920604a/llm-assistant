from api.routers import chat_history, dashboard, query, setting
from core.middleware import setup_middlewares
from fastapi import FastAPI

app = FastAPI(title="MCP Client Service")

# === 設定中間件 ===
setup_middlewares(app)


app.include_router(query.router, tags=["query"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(setting.router, tags=["setting"])
app.include_router(chat_history.router, tags=["chat_history"])
