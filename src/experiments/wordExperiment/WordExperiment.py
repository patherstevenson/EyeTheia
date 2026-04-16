import threading
import time

import GazeManager
import mediapipe as mp
import asyncio

from experiments.wordExperiment import WordGroup
from experiments.wordExperiment.GroupResults import GroupResults
from ui import AppState
from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT


class WordExperiment:
    def __init__(self, state: AppState):
        self.word_groups = state.word_groups

        self.actual_index = 0
        self.gaze_manager: GazeManager = state.gaze_manager
        self.running = False
        self.last_coords = None
        self._thread = None
        self._listeners = {}
        self.results: list[GroupResults] = state.results
        self.state: AppState = state
        self.last_group_date = time.time()

    async def start(self):
        if self.running:
            return

        self.running = True
        self._thread = threading.Thread(target=asyncio.run, args=(self._run_loop(),), daemon=True)
        self._thread.start()

        self.actual_index = 0

        await self.set_word_group()

    def add_finish_listener(self, finish_listener):
        self._listeners["finish"] = finish_listener

    def add_listener(self, listener):
        self._listeners["coords"] = listener

    def stop(self):
        self.running = False

    async def _run_loop(self):
        with mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1) as face_mesh:
            while self.running:
                cx, cy = self.gaze_manager.getGazeCoords(face_mesh)
                self.last_coords = (cx, cy)
                self._listeners["coords"](cx, cy)

                if len(self.results) > self.actual_index is not None:
                    self.results[self.actual_index].gaze_score[self.get_button_index()] += 1

                if (time.time() - self.last_group_date >= self.state.settings.max_time_to_choose):
                    await self.choose(-1)

    def get_button_index(self):
        """Return button index based on where the patient is looking
        :return : The index of the looked button. 4 if no face is detected"""
        (cx, cy) = self.last_coords
        if (cx == -1 & cy == -1):
            return 4
        else:
            result = 0
            if cx > (SCREEN_WIDTH / 2):
                result = result + 1
            if cy > (SCREEN_HEIGHT / 2):
                result = result + 2

            return result

    def has_current_group(self):
        return self.actual_index < len(self.word_groups)

    def get_current_group(self) -> WordGroup:
        if not self.has_current_group():
            return None
        return self.word_groups[self.actual_index]

    def get_current_words(self):
        current_group = self.get_current_group()
        if current_group is None:
            return []
        return current_group.words

    def get_current_sound(self):
        current_group = self.get_current_group()
        if current_group is None:
            return ""
        return current_group.sound

    def is_finished(self):
        return not self.has_current_group()

    async def new_group(self):
        self.actual_index += 1

        await self.set_word_group()

    async def set_word_group(self):
        await self._listeners["show_word_group"]()
        self.results.append(GroupResults(self.actual_index, self.get_current_group()))
        self.results[self.actual_index] = GroupResults(self.actual_index, self.get_current_group())

    async def choose(self, index):

        self.results[self.actual_index].selected = index

        if (self.actual_index < len(self.word_groups) - 1):
            self._listeners["show_plus"]()
            await asyncio.sleep(self.state.settings.time_to_wait_between)
            self.last_group_date = time.time()
            await self.new_group()

        else:
            self._listeners["finish"]()
