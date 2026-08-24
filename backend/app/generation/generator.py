from app.ai.provider import FallbackAIProvider
from app.config import settings


UNCERTAINTY_RESPONSE = {
    "answer": "I couldn't find enough information in the uploaded documents to answer that confidently.",
    "confidence": 0.0,
    "citations": [],
}


class AnswerGenerator:
    def __init__(self):
        self._provider = FallbackAIProvider()

    def generate(self, question: str, chunks: list[dict], document_id: str) -> dict:
        if not chunks:
            return UNCERTAINTY_RESPONSE.copy()

        context_parts = []
        for chunk in chunks:
            context_parts.append(f"[Page {chunk['page_number']}] {chunk['text']}")
        context = "\n\n".join(context_parts)

        prompt = (
            f"Question: {question}\n\n"
            f"Document excerpts:\n{context}\n\n"
            "Answer using ONLY the document excerpts above. "
            "Cite page numbers (e.g., 'According to page 2...'). "
            "If the answer is not covered by the excerpts, say so explicitly."
        )
        system_prompt = (
            "You are a precise support agent. Answer questions using only the provided document excerpts. "
            "Never fabricate information. Always cite the page number from the excerpts."
        )

        try:
            response = self._provider.generate(prompt, system_prompt=system_prompt, temperature=0.1, max_tokens=512)
            answer_text = response.text
        except Exception as exc:
            answer_text = f"An error occurred generating the answer: {exc}"

        confidence = sum(c["score"] for c in chunks) / len(chunks)

        citations = [
            {
                "page_number": c["page_number"],
                "chunk_text": c["text"][:200],
                "score": c["score"],
                "rank": c["rank"],
            }
            for c in chunks
        ]

        return {"answer": answer_text, "confidence": confidence, "citations": citations}
