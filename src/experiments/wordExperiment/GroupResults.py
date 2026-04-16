class GroupResults:
    """
    Represent the result of a Group of Words
    """

    def __init__(self, index: int, words: list[str], selected: int = - 1):
        """
        Init a GroupResult
        :param index: the index of the group in the whole dataset
        :param words: the words shown in the group
        :param selected: the index of the selected word. -1 means no word were chosen yet
        """
        self.index: int = index
        self.words: list[str] = words
        self.selected: int = selected
        self.gaze_score: list[int] = [0,0,0,0]

    def get_selected_word(self):
        """Return directly the selected word, not just his index in the group."""
        return self.words[self.selected]


    def __str__(self):
        return str(self.index) + " : " + str(self.words) + " | " + self.get_selected_word()
