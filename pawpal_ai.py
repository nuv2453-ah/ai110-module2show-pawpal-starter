"""
pawpal_ai.py — RAG + Groq LLM integration for PawPal+

Orchestrates:
  1. Safety guardrail (reject harmful queries)
  2. RAG retrieval from the knowledge base
  3. Groq API call (free) with retrieved context
  4. Confidence score parsing
  5. Structured logging
"""

import os
import logging
from pathlib import Path

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from groq import Groq

from rag_store import build_index, retrieve, format_context

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pawpal.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Safety guardrail — block queries that seek to harm pets
# ---------------------------------------------------------------------------
_HARMFUL_PATTERNS = [
    "how to poison",
    "how to hurt",
    "how to kill",
    "how to harm",
    "make my pet sick",
]


def is_safe_query(query: str) -> bool:
    """Return False if the query appears to seek harmful advice."""
    lowered = query.lower()
    return not any(pattern in lowered for pattern in _HARMFUL_PATTERNS)


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
_SYSTEM_INSTRUCTIONS = (
    "You are PawPal+, a knowledgeable and caring pet care assistant. "
    "Answer questions ONLY using the provided knowledge base context. "
    "If the context does not contain enough information to answer confidently, "
    "say so clearly and recommend the owner consult their vet. "
    "Always prioritize pet safety above all else. "
    "Keep your answer concise (3-5 sentences). "
    "On the very last line of your response, output your confidence score "
    "in this exact format with no extra text: CONFIDENCE: 0.X"
)


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------
def ask_pawpal(
    question: str,
    pet_name: str = "",
    species: str = "",
    index: list[dict] | None = None,
    top_k: int = 3,
) -> dict:
    """
    Answer a pet care question using RAG + Groq.

    Returns a dict with keys:
        answer      (str)   — the AI's answer
        sources     (list)  — knowledge base docs that were retrieved
        confidence  (float) — 0.0–1.0 self-reported confidence
        safe        (bool)  — False if the guardrail blocked the query
        error       (str)   — non-empty only if something went wrong
    """
    # 1. Guardrail
    if not is_safe_query(question):
        logger.warning("Guardrail blocked query: %s", question)
        return {
            "answer": (
                "I can only help with responsible pet care questions. "
                "Please consult a vet if your pet needs urgent care."
            ),
            "sources": [],
            "confidence": 0.0,
            "safe": False,
            "error": "",
        }

    # 2. RAG retrieval
    if index is None:
        index = build_index()

    retrieved = retrieve(question, index, top_k=top_k)
    context = format_context(retrieved)
    sources = list({chunk["source"] for chunk in retrieved})
    logger.info("Query: %r | Retrieved sources: %s", question, sources)

    # 3. Build messages
    pet_context = ""
    if pet_name and species:
        pet_context = f"The owner is asking about their {species} named {pet_name}.\n\n"
    elif species:
        pet_context = f"The owner has a {species}.\n\n"

    user_message = (
        f"{pet_context}"
        f"Knowledge base context:\n{context}\n\n"
        f"Question: {question}"
    )

    # 4. Call Groq
    try:
        client = Groq()  # reads GROQ_API_KEY from environment / .env

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=512,
            messages=[
                {"role": "system", "content": _SYSTEM_INSTRUCTIONS},
                {"role": "user",   "content": user_message},
            ],
        )
    except Exception as exc:
        logger.error("Groq API call failed: %s", exc)
        return {
            "answer": f"An error occurred while contacting the AI: {exc}",
            "sources": sources,
            "confidence": 0.0,
            "safe": True,
            "error": str(exc),
        }

    # 5. Parse response and confidence score
    raw = response.choices[0].message.content
    confidence = 0.5
    answer = raw

    if "CONFIDENCE:" in raw:
        body, _, score_part = raw.rpartition("CONFIDENCE:")
        answer = body.strip()
        try:
            confidence = max(0.0, min(1.0, float(score_part.strip())))
        except ValueError:
            pass

    logger.info(
        "Confidence: %.2f | Tokens in/out: %d/%d",
        confidence,
        response.usage.prompt_tokens,
        response.usage.completion_tokens,
    )

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "safe": True,
        "error": "",
    }


# ---------------------------------------------------------------------------
# Quick CLI smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    idx = build_index()
    test_qs = [
        ("How often should I feed my adult dog?", "Buddy", "dog"),
        ("Is ibuprofen safe to give my cat?", "Whiskers", "cat"),
        ("What do I do if my pet misses a medication dose?", "", ""),
    ]
    for q, name, sp in test_qs:
        print(f"\nQ: {q}")
        result = ask_pawpal(q, pet_name=name, species=sp, index=idx)
        print(f"A: {result['answer']}")
        print(f"   Sources: {result['sources']}  |  Confidence: {result['confidence']:.2f}")
