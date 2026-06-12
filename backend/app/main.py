import sys
import types
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Dynamic imports mapping to resolve LangChain version migration issues globally
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    try:
        from langchain_community.chat_models import ChatOpenAI
    except ImportError:
        ChatOpenAI = None

try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    ChatPromptTemplate = None

try:
    from langchain_core.output_parsers import JsonOutputParser
except ImportError:
    JsonOutputParser = None

# Create module wrappers to intercept older namespace imports
mock_chat_models = types.ModuleType("langchain.chat_models")
mock_chat_models.ChatOpenAI = ChatOpenAI
sys.modules['langchain.chat_models'] = mock_chat_models

mock_prompts = types.ModuleType("langchain.prompts")
mock_prompts.ChatPromptTemplate = ChatPromptTemplate
sys.modules['langchain.prompts'] = mock_prompts

mock_output_parsers = types.ModuleType("langchain.output_parsers")
mock_output_parsers.JsonOutputParser = JsonOutputParser
sys.modules['langchain.output_parsers'] = mock_output_parsers

from app.api.routers import replay

app = FastAPI(
    title="Council AI Hedge Fund API",
    description="Backend API server for Council, the AI investment committee debate and trading platform.",
    version="1.0"
)

# Enable CORS for frontend Next.js dashboard integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Wildcard for hackathon flexibility, can restrict to specific domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(replay.router, prefix="/api")

@app.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Council AI Hedge Fund Backend",
        "version": "1.0"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
