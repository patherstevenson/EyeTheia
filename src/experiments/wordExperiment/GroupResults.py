from experiments.wordExperiment.WordGroup import WordGroup
from experiments.wordExperiment.GazePoint import GazePoint



class GroupResults:
    """
    Represent the result of a Group of Words
    """

    def __init__(self, index: int, words: WordGroup, selected: int = - 1, total_time: int = 0):
        """
        Init a GroupResult
        :param index: the index of the group in the whole dataset
        :param words: the words shown in the group
        :param selected: the index of the selected word. -1 means no word were chosen yet
        """
        self.index: int = index
        self.words: WordGroup = words
        self.selected: int = selected
        self.gaze_score: list[int] = [0, 0, 0, 0, 0]
        self.gaze_points: list[GazePoint] = []
        self.total_time: int = total_time

    def get_selected_word(self):
        """Return directly the selected word, not just his index in the group."""
        return self.words.words[self.selected]

    def __str__(self):
        # return str(self.index) + " : " + str(self.words.words) + " | " + self.get_selected_word() + " | " + str(self.gaze_score) + "\n" + str(self.gaze_points)
        result = "["
        for pt in self.gaze_points:
            result = result + str(pt)

        return f"state.results[1].gaze_score = {result}]\n\n"
