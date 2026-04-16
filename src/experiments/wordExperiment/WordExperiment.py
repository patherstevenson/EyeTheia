import threading
import time

import GazeManager
import mediapipe as mp
import asyncio

from experiments.wordExperiment import WordGroup
from experiments.wordExperiment.GroupResults import GroupResults
from ui import AppState


class WordExperiment:
    def __init__(self, state: AppState):
        self.word_groups = state.word_groups

        self.actual_index = 0
        self.gaze_manager: GazeManager = state.gaze_manager
        self.running = False
        self.last_coords = None
        self._thread = None
        self._listeners = {}
        self.results: dict[GroupResults] = {}
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
                if (time.time() - self.last_group_date >= self.state.settings.max_time_to_choose):
                    await self.choose(-1)

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
        self.results[self.actual_index] = GroupResults(self.actual_index, self.get_current_group().words)

    async def choose(self, index):

        self.results[self.actual_index].selected = index

        if (self.actual_index < len(self.word_groups) - 1):
            self._listeners["show_plus"]()
            await asyncio.sleep(self.state.settings.time_to_wait_between)
            self.last_group_date = time.time()
            await self.new_group()

        else:
            self._listeners["finish"]()
