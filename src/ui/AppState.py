from dataclasses import dataclass, field

from GazeManager import GazeManager
from experiments.wordExperiment.WordGroup import WordGroup
from ui.AppSettings import WordExperimentSettings


@dataclass
class AppState:
    gaze_manager: GazeManager
    settings: WordExperimentSettings
    word_groups: list[WordGroup] = field(default_factory=list)

    def set_word_groups(self, new_word_groups: list[WordGroup]):
        self.word_groups.clear()
        self.word_groups.extend(new_word_groups)
