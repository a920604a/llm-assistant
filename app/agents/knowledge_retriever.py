
def retrieve_docs(query):
    # TODO: 加入 hybrid search + fastembed
    return ["[相關文件段落1]", "[段落2]"]


def format_context(context_docs):
    return "\n".join(context_docs)