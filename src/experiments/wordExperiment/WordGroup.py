from dataclasses import dataclass, field


@dataclass
class WordGroup:
    words: list[str] = field(default_factory=list)
    correct: str = ""
    sound: str = ""

    def __init__(self, words: list[str] = None, correct: str = "", sound: str = ""):
        if words is not None:
            self.words = words
        else:
            self.words = ["", "", "", ""]
        self.correct = correct
        self.sound = sound

    def toCSV(self):
        csv_str = ",".join(self.words)

        csv_str += self.correct
        csv_str += self.sound

        return csv_str

    def __str__(self):
        return str(self.words) + " | " + self.sound + " | " + self.correct
