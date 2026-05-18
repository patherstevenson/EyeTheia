from dataclasses import dataclass, field

from GazeManager import GazeManager
from experiments.wordExperiment.GroupResults import GroupResults
from experiments.wordExperiment.WordGroup import WordGroup
from ui.AppSettings import WordExperimentSettings


@dataclass
class AppState:
    """Class reuniting the GazeManager, all the experience's settings, the word_groups and the previous results. Usually shared in "page.data" """
    gaze_manager: GazeManager
    settings: WordExperimentSettings
    word_groups: list[WordGroup] = field(default_factory=list)
    results: list[GroupResults] = field(default_factory=list)

    def set_word_groups(self, new_word_groups: list[WordGroup]):
        """Replaces old word_groups with new ones"""
        self.word_groups.clear()
        self.word_groups.extend(new_word_groups)
