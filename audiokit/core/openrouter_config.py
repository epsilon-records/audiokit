from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import torch

def configure_openrouter(api_key: str):
    """Configure OpenRouter settings for LlamaIndex."""
    # Set up OpenRouter as an OpenAI-compatible endpoint
    llm = OpenAILike(
        api_key=api_key,
        api_base="https://openrouter.ai/api/v1",
        model="openai/gpt-3.5-turbo",  # Default model
        temperature=0.7,
        max_tokens=2048,
    )
    
    # Use BAAI/bge-large-en-v1.5 with 1024 dimensions
    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-large-en-v1.5",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    
    return llm, embed_model 