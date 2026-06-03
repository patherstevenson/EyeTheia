from experiments.wordExperiment.GazePoint import GazePoint
from experiments.wordExperiment.WordGroup import WordGroup
from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT


class GroupResults:
    """
    Represent the result of a Group of Words
    """

    def __init__(self, index: int, words: WordGroup, selected: int = - 1, total_time: float = 0, gaze_score: list[int] = None, gaze_points=None, window_width=SCREEN_WIDTH, window_height=SCREEN_HEIGHT):
        """
        Init a GroupResult
        :param index: the index of the group in the whole dataset
        :param words: the words shown in the group
        :param selected: the index of the selected word. -1 means no word were chosen yet
        """
        if gaze_points is None:
            gaze_points = []
        self.index: int = index
        self.word_group: WordGroup = words
        self.selected: int = selected
        self.total_time: float = total_time
        if gaze_score is not None:
            self.gaze_score: list[int] = gaze_score
        else:
            self.gaze_score = [0, 0, 0, 0, 0]
        self.gaze_points: list[GazePoint] = gaze_points

        self.screen_width = window_width
        self.screen_height = window_height

    def get_selected_word(self):
        """Return directly the selected word, not just his index in the group."""
        return self.word_group.words[self.selected]

    def __str__(self):
        result = "["
        for pt in self.gaze_points:
            result = result + str(pt)

        return f"state.results[1].gaze_score = {result}]\n\n"
