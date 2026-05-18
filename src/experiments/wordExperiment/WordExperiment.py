import asyncio
import threading
import time

from GazeManager import GazeManager
import mediapipe as mp
from experiments.wordExperiment.GazePoint import GazePoint
from experiments.wordExperiment.GroupResults import GroupResults
from ui.AppState import AppState
from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT


class WordExperiment:
    def __init__(self, state: AppState):
        self.word_groups = state.word_groups

        self.actual_index = 0
        self.gaze_manager: GazeManager = state.gaze_manager
        self.running = False
        self.last_coords = None
        self._thread = None
        self.listeners = {}
        self.state: AppState = state
        self.last_group_date = time.time()

    async def start(self):
        if self.running:
            return

        self.running = True
        self._thread = threading.Thread(target=asyncio.run, args=(self._run_loop(),), daemon=True)
        self._thread.start()

        self.actual_index = 0

        self.state.results = []

        await self.next_words()

    def add_finish_listener(self, finish_listener):
        self.listeners["finish"] = finish_listener

    def add_listener(self, listener):
        self.listeners["coords"] = listener

    def stop(self):
        self.running = False

    async def _run_loop(self):
        last_gaze = time.time()
        with mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1) as face_mesh:
            while self.running:
                cx, cy = self.gaze_manager.getGazeCoords(face_mesh)
                self.last_coords = (cx, cy)
                self.listeners["coords"](cx, cy)

                if self.state.settings.gaze_per_second != 0:
                    to_wait_between_gaze = (1 / self.state.settings.gaze_per_second)

                    if (len(self.state.results) > 0) & ((time.time() - last_gaze * 1.0) >= to_wait_between_gaze):
                        self.state.results[-1].gaze_score[self.get_button_index()] += 1

                        self.state.results[-1].gaze_points.append(GazePoint(len(self.state.results[-1].gaze_points), cx, cy))
                        last_gaze = time.time()

                if time.time() - self.last_group_date >= self.state.settings.max_time_to_choose:
                    await self.next_words()

    def get_button_index(self):
        """Return button index based on where the patient is looking
        :return : The index of the looked button. 4 if no face is detected"""
        (cx, cy) = self.last_coords
        if cx == -1 & cy == -1:
            return 4
        else:
            result = 0
            if cx > (SCREEN_WIDTH / 2):
                result = result + 1
            if cy > (SCREEN_HEIGHT / 2):
                result = result + 2

            return result

    def get_current_words(self):
        """Return actual words"""
        words = self.word_groups[len(self.state.results) - 1].words
        if words is not None:
            return words
        else:
            return []

    def get_current_sound(self):
        """Return actual words"""
        words = self.word_groups[len(self.state.results) - 1].sound
        if words is not None:
            return words
        else:
            return []

    async def next_words(self, chosen=-1):
        """Show the next word group, and process result if given
        :param chosen : Chosen word in the previous group. If no word was clicked, chosen == -1. If first group, chosen == -2
        """

        if chosen >= 0:
            # Any result given (no auto-skip or first group)
            self.state.results[-1].selected = chosen

        if len(self.word_groups) > len(self.state.results):
            # Show next group
            new_index = len(self.state.results)

            total_time = time.time() - self.last_group_date

            self.listeners["show_plus"]()
            await asyncio.sleep(self.state.settings.time_to_wait_between)

            new_word_group = self.word_groups[new_index]
            self.state.results.append(GroupResults(new_index, new_word_group, chosen, total_time))

            await self.listeners["show_word_group"]()
            self.last_group_date = time.time()


        else:
            self.listeners["finish"]()
