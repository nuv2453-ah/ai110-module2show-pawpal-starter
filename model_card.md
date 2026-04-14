# Model Card — PawPal+ AI

## System Overview

**Model used:** Claude Haiku (`claude-haiku-4-5-20251001`) via the Anthropic API  
**Task type:** Retrieval-Augmented Generation (RAG) — pet care question answering  
**Knowledge base:** 3 curated markdown documents (dog care, cat care, medication guidelines)  
**Retrieval method:** Keyword-frequency scoring over chunked documents

---

## 1. Limitations and Biases

**Knowledge scope:** The system can only answer questions covered by the three knowledge base documents. Questions about exotic pets (birds, reptiles, fish), breed-specific behavior, or complex medical diagnoses will either return low-confidence answers or recommend consulting a vet. This is intentional but limits the system's usefulness for a broader user base.

**Retrieval method:** Keyword matching does not understand semantic similarity. A question like "My dog won't touch its food" may not retrieve feeding guidelines if the word "feed" doesn't appear in the query. Embedding-based retrieval would handle this better.

**Confidence calibration:** The confidence scores are self-reported by Claude based on a prompt instruction. They reflect the model's perceived certainty, not a statistically calibrated probability. Users should treat them as a directional signal, not a guarantee.

**Species and size bias:** The knowledge base focuses on adult dogs and cats. It underrepresents puppies/kittens, senior pets, small vs. large breed differences, and multi-pet household dynamics.

**Cultural and regional bias:** The knowledge base reflects North American pet care conventions (e.g., specific vaccines, vet visit frequencies). Guidelines may differ in other countries.

---

## 2. Potential Misuse and Prevention

**Risk — Replacing professional veterinary advice:** Users might rely on PawPal+ for medical decisions that require a vet (e.g., diagnosing illness, adjusting medication dosages). This could lead to delayed treatment.

**Mitigation:**
- The system prompt explicitly instructs Claude to recommend consulting a vet when the knowledge base lacks sufficient information.
- Low-confidence responses (below ~0.7) prompt extra caution in the UI.
- The system never claims to replace a veterinarian.

**Risk — Harmful intent:** A user could try to extract information about substances that harm animals.

**Mitigation:**
- The guardrail in `pawpal_ai.py` blocks queries matching harmful intent patterns (`"how to poison"`, `"how to hurt"`, etc.) before any retrieval or API call.
- The guardrail is a lightweight first-pass filter; it is not exhaustive and should be combined with Anthropic's built-in safety features.

**Risk — Incorrect medication guidance:** Pets have significant weight- and species-based dosage differences. The system does not know a pet's weight or full medical history.

**Mitigation:**
- The knowledge base provides general guidelines only, not dosage-specific instructions.
- The system always directs medication questions to a vet for specifics.

---

## 3. Testing Surprises

**Surprise 1 — Guardrail robustness:** The simple keyword-pattern guardrail worked reliably for obvious harmful queries but would not catch subtle or indirect rephrasing (e.g., "what amount of ibuprofen would be dangerous for a 10lb dog?"). The second form is actually a legitimate safety question, illustrating the challenge of distinguishing harmful from protective intent.

**Surprise 2 — Confidence scoring consistency:** Claude's self-reported confidence was notably consistent across runs on the same query (±0.03). This was unexpected — the score converged to a stable estimate even though the model was generating it stochastically.

**Surprise 3 — Retrieval quality matters more than prompting:** Rewriting the system prompt had marginal impact on answer quality. Adding one well-structured paragraph to the knowledge base documents produced a larger improvement. This confirms the principle that in RAG systems, retrieval quality is the primary lever.

**Surprise 4 — Prompt caching latency:** The second query in a session was measurably faster than the first (~30% reduction in response time). The cache hit was visible in the API usage logs (`cache_read_input_tokens > 0`).

---

## 4. AI Collaboration

### Helpful AI suggestion

When designing the `retrieve()` function in `rag_store.py`, the AI suggested using paragraph-level chunking with an overlap buffer rather than fixed-character chunking. This was the right call — paragraphs in the markdown knowledge base are natural semantic units (e.g., "Feeding" section, "Medications" section), so paragraph chunks preserve context much better than arbitrary character splits. The retrieval results were noticeably more coherent with this approach.

### Flawed AI suggestion

The AI initially suggested building the RAG index with `sentence-transformers` embeddings stored in a local `chromadb` vector database. While this would improve retrieval quality, it introduced four new heavyweight dependencies (torch, sentence-transformers, chromadb, hnswlib) and would have required a GPU-compatible environment or slow CPU inference. For a demo with only 3 documents and ~50 chunks, this was massive over-engineering. I replaced it with simple keyword scoring, which is faster to set up, has zero additional dependencies, and works well enough for the knowledge base size. The lesson: AI suggestions often optimize for maximum technical sophistication, not for the actual problem constraints.

---

## 5. What This Project Says About Me as an AI Engineer

> I approach AI systems as tools that need to earn trust — through transparency (showing sources), honest uncertainty (confidence scores), and safe failure modes (guardrails, vet referrals). I'm comfortable building end-to-end systems that integrate retrieval, LLM APIs, evaluation, and a real user interface, and I understand that the reliability of an AI system is determined more by its architecture and data quality than by the model choice alone.
