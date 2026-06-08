import asyncio
import threading
import time

import mediapipe as mp
from experiments.wordExperiment.GazePoint import GazePoint
from experiments.wordExperiment.GroupResults import GroupResults
from ui.AppState import AppState
from ui.FletUtils import playSound
from utils.config import SCREEN_WIDTH, SCREEN_HEIGHT


def get_button_index_from_coords(cx, cy):
    """Return button index based on where the user is looking
    :return : The index of the looked button. 4 if no face is detected"""
    if cx == -1 & cy == -1:
        return 4
    else:
        result = 0
        if cx > (SCREEN_WIDTH / 2):
            result = result + 1
        if cy > (SCREEN_HEIGHT / 2):
            result = result + 2

        return result


class WordExperiment:
    def __init__(self, state: AppState, show_plus, show_words, finish, ):
        self.thread = None
        self.gaze_thread = None
        self.current_word_group = None
        self.group_start_time = time.time()
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
        self.state = state
        self.index = 0
        self.show_plus = show_plus
        self.show_words = show_words
        self.finish = finish

        self.time_between_gaze = 1 / state.settings.gaze_per_second if state.settings.gaze_per_second else 0

        self.running = False
        self.group_done = threading.Event()
        self.selected = -1

    def start(self):
        if self.running:
            return

        self.running = True
        self.state.results = []
        self.thread = threading.Thread(target=asyncio.run, args=(self.main_loop(),), daemon=True)
        self.thread.start()

    async def main_loop(self):
        for index, group in enumerate(self.state.word_groups):
            if not self.running:
                break

            self.index = index
            self.current_word_group = group
            self.selected = -1
            self.group_done.clear()
            self.group_start_time = time.time()

            self.show_plus()
            await asyncio.sleep(self.state.settings.time_to_wait_between)

            if not self.running:
                break

            self.state.results.append(GroupResults(index, group))
            self.group_start_time = time.time()
            self.show_words(group)

            await playSound(group.sound)
            self.gaze_thread = threading.Thread(target=self.gaze_loop, daemon=True)
            self.gaze_thread.start()

            last_sound = time.time()
            sound_cpt = self.state.settings.sound_repeat - 1

            while self.running and not self.group_done.is_set():
                elapsed = time.time() - self.group_start_time

                if elapsed >= self.state.settings.max_time_to_choose:
                    self.next_group()
                    break

                if sound_cpt > 0 and time.time() - last_sound >= self.state.settings.sound_interval:
                    await playSound(group.sound)
                    last_sound = time.time()
                    sound_cpt -= 1

                await asyncio.sleep(0.02)

            if self.gaze_thread is not None:
                self.gaze_thread.join(timeout=1)

        self.running = False
        self.finish()

    def next_group(self, value: int = -1):
        if not self.running or self.group_done.is_set() or self.index >= len(self.state.results):
            return

        self.state.results[self.index].index = self.index
        self.state.results[self.index].word_group = self.current_word_group
        self.state.results[self.index].selected = value
        self.state.results[self.index].total_time = time.time() - self.group_start_time

        self.selected = value
        self.group_done.set()

    def gaze_loop(self):
        """Run a loop in a different thread to store every points the user looked at"""

        print("gaze_loop")

        if self.time_between_gaze <= 0:
            return

        cpt = 0
        last_gaze = time.time()

        self.state.results[self.index].gaze_score = [0, 0, 0, 0, 0]
        while self.running and not self.group_done.is_set():
            next_gaze_date = last_gaze + self.time_between_gaze
            time_to_sleep = next_gaze_date - time.time()
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

            (x, y) = self.state.gaze_manager.getGazeCoords(self.face_mesh)

            last_gaze = time.time()

            self.state.results[self.index].gaze_points.append(GazePoint(cpt, x, y))

            self.state.results[self.index].gaze_score[get_button_index_from_coords(x, y)] += 1

            cpt += 1
