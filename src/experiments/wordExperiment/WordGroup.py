from dataclasses import dataclass, field

@dataclass
class WordGroup:
    words: list[str] = field(default_factory=list)
    correct: str = ""
    sound: str = ""