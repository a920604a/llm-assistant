import json
import logging
from typing import Iterator

import httpx

import gradio as gr

logger = logging.getLogger(__name__)

# ==========================
# Configuration
# ==========================
API_BASE_URL = "http://localhost:8022/api/v1/gradio"
DEFAULT_MODEL = "gpt-oss:20b"
AVAILABLE_CATEGORIES = ["cs.AI", "cs.LG"]


# ==========================
# Async streaming response
# ==========================
async def stream_response(
    query: str, top_k: int = 3, use_hybrid: bool = True, model: str = DEFAULT_MODEL
) -> Iterator[str]:
    """Stream response from the RAG API."""
    if not query.strip():
        yield "⚠️ Please enter a question."
        return

    payload = {"query": query, "top_k": top_k, "use_hybrid": use_hybrid, "model": model}

    try:
        url = f"{API_BASE_URL}/stream"
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", url, json=payload, headers={"Accept": "text/plain"}
            ) as response:
                if response.status_code != 200:
                    yield f"❌ Error: API returned status {response.status_code}"
                    return

                current_answer = ""
                sources = []
                chunks_used = 0
                search_mode = ""

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                        data_str = line[6:]  # Remove "data: " prefix

                        try:
                            data = json.loads(data_str)

                            # Handle error
                            if "error" in data:
                                yield f"❌ Error: {data['error']}"
                                return

                            # Handle metadata
                            if "sources" in data:
                                sources = data["sources"]
                                chunks_used = data.get("chunks_used", 0)
                                search_mode = data.get("search_mode", "unknown")
                                continue

                            # Handle streaming chunks
                            if "chunk" in data or "response" in data:
                                current_answer += data["chunk"]
                                formatted_response = current_answer
                                if sources or chunks_used:
                                    formatted_response += "\n\n**🔎 Search Info:**\n"
                                    formatted_response += f"- Mode: {search_mode}\n"
                                    formatted_response += (
                                        f"- Chunks used: {chunks_used}\n"
                                    )
                                    if sources:
                                        formatted_response += (
                                            f"- Sources: {len(sources)} papers\n"
                                        )
                                        for i, source in enumerate(sources[:3], 1):
                                            formatted_response += f"  {i}. [{source.split('/')[-1]}]({source})\n"
                                        if len(sources) > 3:
                                            formatted_response += (
                                                f"  ... and {len(sources) - 3} more\n"
                                            )
                                yield formatted_response

                            # Handle completion
                            if data.get("done", False):
                                final_answer = data.get("answer", current_answer)
                                if final_answer != current_answer:
                                    current_answer = final_answer

                                formatted_response = current_answer
                                if sources or chunks_used:
                                    formatted_response += "\n\n**🔎 Search Info:**\n"
                                    formatted_response += f"- Mode: {search_mode}\n"
                                    formatted_response += (
                                        f"- Chunks used: {chunks_used}\n"
                                    )
                                    if sources:
                                        formatted_response += (
                                            f"- Sources: {len(sources)} papers\n"
                                        )
                                        for i, source in enumerate(sources[:3], 1):
                                            formatted_response += f"  {i}. [{source.split('/')[-1]}]({source})\n"
                                        if len(sources) > 3:
                                            formatted_response += (
                                                f"  ... and {len(sources) - 3} more\n"
                                            )

                                yield formatted_response
                                break

                        except json.JSONDecodeError:
                            continue

    except httpx.RequestError as e:
        yield f"⚠️ Connection error: {str(e)}\nMake sure the API server is running at {API_BASE_URL}"
    except Exception as e:
        yield f"❌ Unexpected error: {str(e)}"


# ==========================
# Gradio Interface
# ==========================
def create_interface():
    """Create and configure the Gradio interface."""
    with gr.Blocks(
        title="arXiv Paper Assistance - RAG Chat", theme=gr.themes.Soft()
    ) as interface:
        gr.Markdown(
            """
            # 🔬 arXiv Paper Assistance - RAG Chat

            Ask questions about machine learning and AI research papers from arXiv.
            The system will search through indexed papers and provide answers with sources.
            """
        )

        with gr.Row():
            with gr.Column(scale=3):
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="What are transformers in machine learning?",
                    lines=2,
                    max_lines=5,
                )
            with gr.Column(scale=1):
                submit_btn = gr.Button("Ask Question", variant="primary", size="lg")

        with gr.Row():
            with gr.Column():
                with gr.Accordion("Advanced Options", open=False):
                    top_k = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=3,
                        step=1,
                        label="Number of chunks to retrieve",
                        info="More chunks = more context but slower generation",
                    )

                    use_hybrid = gr.Checkbox(
                        value=True,
                        label="Use hybrid search",
                        info="Vector embeddings + metadata filtering for better results",
                    )

                    model_choice = gr.Dropdown(
                        choices=[DEFAULT_MODEL],
                        value=DEFAULT_MODEL,
                        label="LLM Model",
                        info="Larger models may give better answers but are slower",
                    )

        response_output = gr.Markdown(
            label="Answer",
            value="Ask a question to get started!",
            height=400,
            elem_classes=["response-markdown"],
        )

        # Examples
        gr.Examples(
            examples=[
                ["What are transformers in machine learning?", 3, True, DEFAULT_MODEL],
                ["How do convolutional neural networks work?", 5, True, DEFAULT_MODEL],
                [
                    "What is attention mechanism in deep learning?",
                    4,
                    False,
                    DEFAULT_MODEL,
                ],
                ["Explain reinforcement learning algorithms", 3, True, DEFAULT_MODEL],
                ["What are the latest developments in NLP?", 5, True, DEFAULT_MODEL],
            ],
            inputs=[query_input, top_k, use_hybrid, model_choice],
        )

        # Event bindings
        submit_btn.click(
            fn=stream_response,
            inputs=[query_input, top_k, use_hybrid, model_choice],
            outputs=[response_output],
            show_progress=True,
        )
        query_input.submit(
            fn=stream_response,
            inputs=[query_input, top_k, use_hybrid, model_choice],
            outputs=[response_output],
            show_progress=True,
        )

        gr.Markdown(
            """
            ---
            **Note**: Make sure the RAG API server is running at `http://localhost:8000`.

            **Categories**: cs.AI, cs.LG, cs.CL, cs.CV, cs.NE, stat.ML
            """
        )

    return interface


# ==========================
# Main
# ==========================
def main():
    print("🚀 Starting arXiv Paper Curator Gradio Interface...")
    print(f"📡 API Base URL: {API_BASE_URL}")
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True,
        quiet=False,
    )


if __name__ == "__main__":
    main()
