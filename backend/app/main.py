from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import errors
import os

from .search import web_search


# ============================================================
# Load environment variables
# ============================================================

load_dotenv(
    os.path.join(
        os.path.dirname(__file__),
        ".env"
    )
)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found. "
        "Check backend/app/.env"
    )


# ============================================================
# Gemini client
# ============================================================

client = genai.Client(api_key=api_key)


# ============================================================
# FastAPI application
# ============================================================

app = FastAPI(
    title="AI Research Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Request model
# ============================================================

class ResearchRequest(BaseModel):
    question: str


# ============================================================
# Response model
# ============================================================

class ResearchResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]


# ============================================================
# Home endpoint
# ============================================================

@app.get("/")
def home():
    return {
        "message": "AI Research Agent backend is running!"
    }


# ============================================================
# Research endpoint
# ============================================================

@app.post(
    "/research",
    response_model=ResearchResponse
)
def research(request: ResearchRequest):

    question = request.question

    print("\n==============================")
    print("STEP 1: Research started")
    print("Question:", question)
    print("==============================")

    # --------------------------------------------------------
    # Step 1: Web search
    # --------------------------------------------------------

    print("STEP 2: Starting web search...")

    try:
        results = web_search(
            question,
            max_results=5
        )
    except Exception as e:
        print("Web search error:", e)

        return {
            "question": question,
            "answer": f"Web search failed: {str(e)}",
            "sources": []
        }

    print(
        f"STEP 3: Web search completed. "
        f"Found {len(results)} results."
    )

    # --------------------------------------------------------
    # Step 2: Prepare research information
    # --------------------------------------------------------

    sources = []
    research_text = ""

    for i, result in enumerate(results, start=1):

        title = result.get("title", "")
        url = result.get("url", "")
        snippet = result.get("snippet", "")

        if url:
            sources.append(url)

        research_text += f"""
SOURCE {i}
Title: {title}
URL: {url}
Information: {snippet}

"""

    print("STEP 4: Research information prepared.")

    # --------------------------------------------------------
    # Step 3: Create Gemini prompt
    # --------------------------------------------------------

    prompt = f"""
You are an AI Research Assistant.

Answer the user's research question using the
information collected from the web sources below.

User question:
{question}

Web research:
{research_text}

Instructions:

1. Give a clear and useful answer.
2. Use the provided research information.
3. Do not invent facts.
4. If the research information is insufficient,
   clearly say so.
5. Organize the answer with headings or bullet
   points when useful.
6. Keep the answer easy to understand.
"""

    # --------------------------------------------------------
    # Step 4: Ask Gemini
    # --------------------------------------------------------

    print("STEP 5: Gemini request starting...")

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        print("STEP 6: Gemini response received.")

        answer = response.text

        if not answer:
            answer = "Gemini returned an empty response."

    except errors.ServerError as e:

        print("Gemini server error:", e)

        return {
            "question": question,
            "answer": "Gemini is temporarily unavailable. Please try again.",
            "sources": sources
        }

    except Exception as e:

        print("Gemini error:", e)

        return {
            "question": question,
            "answer": "The AI service is temporarily unavailable. Please try again later.",
            "sources": sources
        }

    # --------------------------------------------------------
    # Step 5: Return successful response
    # --------------------------------------------------------

    print("STEP 7: Returning final response.")

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }