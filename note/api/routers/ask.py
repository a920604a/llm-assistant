# REST API routers
import time

from api.auto_metrics import observe_api
from api.schemas.ask import AskRequest, AskResponse, GradioStreamRequest
from api.schemas.query import Query
from api.schemas.SystemSetting import SystemSettings
from arxiv_rag_pipeline import ask_flow, rag_stream
from dependencies import (
    LangfuseDep,
    OllamaDep,
    PaperCacheDep,
    QdrantDep,
    SettingsDep,
    UserCacheDep,
)
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from logger import AppLogger
from services.langfuse.tracer import RAGTracer

logger = AppLogger(__name__).get_logger()


ask_router = APIRouter(tags=["ask"])
stream_router = APIRouter(tags=["stream"])


@ask_router.post("/api/v1/ask", response_model=AskResponse)
@observe_api
async def ask_question(
    request: Query,
    ollama_client: OllamaDep,
    qdrant_client: QdrantDep,
    paper_cache_client: PaperCacheDep,
    user_cache_client: UserCacheDep,
    langfuse_tracer: LangfuseDep,
    settings: SettingsDep,
) -> AskResponse:
    q = request.text.strip()
    logger.info("ask_question %s", q)

    rag_tracer = RAGTracer(langfuse_tracer)
    start_time = time.time()
    system_settings = user_cache_client.get_redis_system_setting(request.user_id)
    top = system_settings.top_k
    lang = system_settings.user_language
    logger.info("ask_question %s, top_k=%s, user_language=%s", q, top, lang)

    ask_r = AskRequest(
        user_id=request.user_id,
        query=request.text,
        top_k=system_settings.top_k,
        use_hybrid=True,
        model=settings.MODEL_NAME,
    )

    with rag_tracer.trace_request(request.user_id, ask_r.query) as trace:
        if paper_cache_client:
            try:
                cached_response = await paper_cache_client.find_cached_response(ask_r)
                if cached_response:
                    logger.info("Returning cached response for exact query match")

                    rag_tracer.end_request(
                        trace, cached_response.answer, time.time() - start_time
                    )
                    return cached_response
            except Exception as e:
                logger.warning(f"Cache check failed, proceeding with normal flow: {e}")

        response = await ask_flow(
            query=q,
            system_settings=system_settings,
            ollama_client=ollama_client,
            qdrant_client=qdrant_client,
            user_id=ask_r.user_id,
            model=ask_r.model,
            rag_tracer=rag_tracer,
            trace=trace,
        )

        # Store response in exact match cache
        if paper_cache_client:
            try:
                await paper_cache_client.store_response(ask_r, response)
            except Exception as e:
                logger.warning(f"Failed to store response in cache: {e}")

        rag_tracer.end_request(trace, response.answer, time.time() - start_time)

        logger.info(f"ask_question response {response}")
        return response


@stream_router.post("/api/v1/stream")
async def ask_question_stream(
    request: Query,
    ollama_client: OllamaDep,
    qdrant_client: QdrantDep,
    user_cache_client: UserCacheDep,
    langfuse_tracer: LangfuseDep,
):
    q = request.text.strip()
    logger.info("ask_question_stream %s", q)

    system_settings = user_cache_client.get_redis_system_setting(request.user_id)
    top = system_settings.top_k
    lang = system_settings.user_language
    logger.info("ask_question_stream %s, top_k=%s, user_language=%s", q, top, lang)

    return StreamingResponse(
        rag_stream(
            ollama_client=ollama_client,
            qdrant_client=qdrant_client,
            query=q,
            system_settings=system_settings,
            user_id=request.user_id,
            langfuse_tracer=langfuse_tracer,
        ),
        media_type="text/event-stream",  # 前端 fetch 會逐段讀取
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@stream_router.post("/api/v1/gradio/stream")
async def ask_question_gradio_stream(
    request: GradioStreamRequest,
    ollama_client: OllamaDep,
    qdrant_client: QdrantDep,
    user_cache_client: UserCacheDep,
    langfuse_tracer: LangfuseDep,
):
    logger.info(f"request {request}")

    settings = SystemSettings(
        user_language="Traditional Chinese",
        translate=True,
        system_prompt="",
        top_k=request.top_k,
        use_rag=True,
        subscribe_email=True,
        reranker_enabled=True,
        temperature=0.3,
        hybrid_search=request.use_hybrid,
    )

    return StreamingResponse(
        rag_stream(
            ollama_client=ollama_client,
            qdrant_client=qdrant_client,
            query=request.query,
            system_settings=settings,
            user_id="gradio user",
            langfuse_tracer=langfuse_tracer,
            categories=request.categories,
        ),
        media_type="text/event-stream",  # 前端 fetch 會逐段讀取
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
