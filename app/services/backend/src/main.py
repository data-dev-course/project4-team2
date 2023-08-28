from fastapi import FastAPI
import logging.config
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from .routers import comment_count,grammar_state,word_collection



load_dotenv()

logger = logging.getLogger("Grammar Error Insight Backend")

# Set logger name to project

logger.info("START Application")

# Tags for representative endpoints
tags = [
    {
        "name": "app",
        "description": "sample CRUD",
    }
]

# Define Fast api and description
app = FastAPI(
    title="Grammar Error Insight Backend",
    description="Grammar Error Insight Backend",
    version="0.0.1",
    openapi_tags=tags,
)

# CORS (Cross-Origin Resource Sharing) Configuration
origins = [
    "http://localhost",
    "http://localhost:5173",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add routers to main
# app.include_router({router_name}, prefix="path")


app.include_router(comment_count.router, prefix="/comment_count", tags=["comment_count"])
app.include_router(grammar_state.router, prefix="/grammar_state", tags=["grammar_state"])



# This path is for health check or test
@app.get("/")
async def root():
    return {"Connect"}

  