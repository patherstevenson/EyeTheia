from dataclasses import dataclass, field

from GazeManager import GazeManager
from experiments.wordExperiment.WordGroup import WordGroup


@dataclass
class AppState:
    gaze_manager: GazeManager
    word_groups: list[WordGroup] = field(default_factory=list)
    settings: object | None = None

    def set_word_groups(self, new_word_groups: list[WordGroup]):
        self.word_groups.clear()
        self.word_groups.extend(new_word_groups)
