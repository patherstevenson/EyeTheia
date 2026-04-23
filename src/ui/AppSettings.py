from dataclasses import dataclass


@dataclass
class WordExperimentSettings:
    max_time_to_choose: int = 5
    time_to_wait_between: float = 0.5
    buttons_size: float = 1.0
    gaze_per_second: int = 5
