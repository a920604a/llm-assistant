# REST API routers
from api.auto_metrics import observe_api
from api.schemas.ask import AskRequest, AskResponse
from api.schemas.query import Query
from arxiv_rag_pipeline import ask_flow, rag_stream
from dependencies import LangchainDep, OllamaDep, PaperCacheDep, QdrantDep
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from logger import AppLogger
from storage.redis_client import get_redis_system_setting

logger = AppLogger(__name__).get_logger()


ask_router = APIRouter(tags=["ask"])
stream_router = APIRouter(tags=["stream"])


@ask_router.post("/api/v1/ask", response_model=AskResponse)
@observe_api
async def ask_question(
    request: Query,
    langchain_client: LangchainDep,
    qdrant_client: QdrantDep,
    paper_cache_client: PaperCacheDep,
) -> AskResponse:
    q = request.text.strip()
    logger.info("ask_question %s", q)

    system_settings = get_redis_system_setting(request.user_id)
    top = system_settings.top_k
    lang = system_settings.user_language
    logger.info("ask_question %s, top_k=%s, user_language=%s", q, top, lang)

    ask_r = AskRequest(
        user_id=request.user_id,
        query=request.text,
        top_k=system_settings.top_k,
        use_hybrid=True,
        model="gpt-oss:20b",
    )

    if paper_cache_client:
        try:
            cached_response = await paper_cache_client.find_cached_response(ask_r)
            if cached_response:
                logger.info("Returning cached response for exact query match")
                return cached_response
        except Exception as e:
            logger.warning(f"Cache check failed, proceeding with normal flow: {e}")

    response = ask_flow(
        query=q,
        system_settings=system_settings,
        langchain_client=langchain_client,
        qdrant_client=qdrant_client,
        user_id=ask_r.user_id,
    )

    # Store response in exact match cache
    if paper_cache_client:
        try:
            await paper_cache_client.store_response(request, response)
        except Exception as e:
            logger.warning(f"Failed to store response in cache: {e}")

    return response


@stream_router.post("/api/v1/stream")
async def ask_question_stream(
    request: Query,
    ollama_client: OllamaDep,
    langchain_client: LangchainDep,
    qdrant_client: QdrantDep,
):
    q = request.text.strip()
    logger.info("ask_question_stream %s", q)

    system_settings = get_redis_system_setting(request.user_id)
    top = system_settings.top_k
    lang = system_settings.user_language
    logger.info("ask_question_stream %s, top_k=%s, user_language=%s", q, top, lang)

    return StreamingResponse(
        rag_stream(
            ollama_client=ollama_client,
            langchain_client=langchain_client,
            qdrant_client=qdrant_client,
            query=q,
            system_settings=system_settings,
            user_id=request.user_id,
        ),
        media_type="text/plain",  # 前端 fetch 會逐段讀取
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
