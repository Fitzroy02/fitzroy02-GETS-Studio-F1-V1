"""
Content Library Management for GETS Studio
Manages creative content items with metadata, tags, and community feedback
"""

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class LibraryItem:
    name: str
    genre: str
    description: str
    author_notes: str
    tags: List[str] = field(default_factory=list)
    likes: int = 0
    dislikes: int = 0

    def add_like(self):
        self.likes += 1

    def add_dislike(self):
        self.dislikes += 1

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)

    def summary(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "genre": self.genre,
            "description": self.description,
            "author_notes": self.author_notes,
            "tags": ", ".join(self.tags),
            "likes": str(self.likes),
            "dislikes": str(self.dislikes),
        }
