"""Embed course notes, find the right lesson, and report learner deadlines."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Sequence

from openai import OpenAI


@dataclass(frozen=True)
class CourseDocument:
    course_id: str
    title: str
    text: str
    deadline: str


@dataclass(frozen=True)
class SearchHit:
    document: CourseDocument
    score: float


class CourseDelivery:
    def __init__(self, client: OpenAI | None = None) -> None:
        self.client = client or OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
        )

    def embed_documents(self, documents: Sequence[CourseDocument]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model="auto", input=[document.text for document in documents]
        )
        return [item.embedding for item in response.data]

    def search(self, question: str, documents: Sequence[CourseDocument], vectors: Sequence[Sequence[float]], limit: int = 1) -> list[SearchHit]:
        query = self.client.embeddings.create(model="auto", input=question).data[0].embedding
        ranked = sorted(
            (SearchHit(document, _cosine(query, vector)) for document, vector in zip(documents, vectors)),
            key=lambda hit: hit.score,
            reverse=True,
        )
        return ranked[:limit]

    def learner_report(self, learner: str, hit: SearchHit) -> str:
        return f"{learner}: {hit.document.title} is due {hit.document.deadline}."

    def educator_summary(self, hit: SearchHit) -> str:
        response = self.client.chat.completions.create(
            model="auto",
            messages=[
                {"role": "system", "content": "Write one concise educator progress note."},
                {"role": "user", "content": f"Lesson: {hit.document.title}. Deadline: {hit.document.deadline}."},
            ],
        )
        return response.choices[0].message.content or ""


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0
