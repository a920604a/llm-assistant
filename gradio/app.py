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


# ==========================
# Async streaming response
# ==========================
async def stream_response(
    query: str, top_k: int = 3, use_hybrid: bool = True
) -> Iterator[str]:
    """Stream response from the RAG API."""
    if not query.strip():
        yield "⚠️ Please enter a question."
        return

    payload = {"query": query, "top_k": top_k, "use_hybrid": use_hybrid}

    try:
        url = f"{API_BASE_URL}/stream"
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", url, json=payload, headers={"Accept": "text/event-stream"}
            ) as response:
                if response.status_code != 200:
                    yield f"❌ Error: API returned status {response.status_code}"
                    return

                current_answer = ""

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix

                        try:
                            data = json.loads(data_str)
                            print(f"Received data chunk: {data}")

                            # Handle error
                            if "error" in data:
                                yield f"❌ Error: {data['error']}"
                                return

                            # Handle streaming chunks
                            if "chunk" in data or "response" in data:
                                current_answer += data["chunk"]
                                yield current_answer

                            # Handle completion
                            if data.get("done", False):
                                final_answer = data.get("answer", current_answer)
                                if final_answer != current_answer:
                                    current_answer = final_answer

                                yield current_answer
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

        response_output = gr.Markdown(
            label="Answer",
            value="Ask a question to get started!",
            height=400,
            elem_classes=["response-markdown"],
        )

        # Event bindings
        submit_btn.click(
            fn=stream_response,
            inputs=[query_input, top_k, use_hybrid],
            outputs=[response_output],
            show_progress=True,
        )
        query_input.submit(
            fn=stream_response,
            inputs=[query_input, top_k, use_hybrid],
            outputs=[response_output],
            show_progress=True,
        )

        gr.Markdown(
            """
            ---
            **Note**: Make sure the RAG API server is running at `http://localhost:8000`.
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
