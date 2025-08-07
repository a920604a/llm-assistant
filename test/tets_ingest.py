from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from your_module import get_embedding  



@pytest.mark.parametrize("use_st", [True, False])
def test_get_embedding_returns_list_of_float(use_st):
    sample_text = "這是一段中文測試文字"

    if use_st:
        # mock SentenceTransformer 的 encode 回傳 numpy array
        with patch("your_module.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = [[0.1, 0.2, 0.3]]
            mock_st.return_value = mock_model

            result = get_embedding(sample_text, use_sentence_transformers=True)
            assert isinstance(result, list)
            assert all(isinstance(x, float) for x in result)
    else:
        # mock TextEmbedding 的 embed 回傳 generator
        with patch("your_module.TextEmbedding") as mock_fe:
            mock_embedder = MagicMock()
            mock_embedder.embed.return_value = iter([[0.4, 0.5, 0.6]])
            mock_fe.return_value = mock_embedder

            result = get_embedding(sample_text, use_sentence_transformers=False)
            assert isinstance(result, list)
            assert all(isinstance(x, float) for x in result)