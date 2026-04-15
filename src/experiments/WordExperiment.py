import threading

import GazeManager
import mediapipe as mp


class WordExperiment:
    def __init__(self, gaze_manager: GazeManager, word_groups):
        self.word_groups = word_groups
        self.actual_index = 0
        self.gaze_manager: GazeManager = gaze_manager
        self.running = False
        self.last_coords = None
        self._thread = None
        self._listeners = []
        self._finish_listener = None
        self.resuts = []

    def add_finish_listener(self, finish_listener):
        self._finish_listener = finish_listener

    def add_listener(self, listener):
        self._listeners.append(listener)

    def _notify(self, cx, cy):
        for listener in self._listeners:
            listener(cx, cy)

    def start(self):
        if self.running:
            return

        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _run_loop(self):
        with mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1) as face_mesh:
            while self.running:
                cx, cy = self.gaze_manager.getGazeCoords(face_mesh)
                self.last_coords = (cx, cy)
                self._notify(cx, cy)

    def has_current_group(self):
        return self.actual_index < len(self.word_groups)

    def get_current_group(self):
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

    def choose(self, index):
        self.resuts.append(index)
        self.actual_index += 1
        if self.is_finished() and self._finish_listener is not None:
            self._finish_listener(None)
