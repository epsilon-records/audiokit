from llama_index.llms import OpenAILike
from llama_index.embeddings import HuggingFaceEmbedding

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
    
    # Use local embeddings instead of OpenAI
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    return llm, embed_model 