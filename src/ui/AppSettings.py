from dataclasses import dataclass
from enum import Enum


@dataclass
class WordExperimentSettings:
    max_time_to_choose: int = 5
    time_to_wait_between: float = 0.5
    buttons_size: float = 0.5
    gaze_per_second: int = 5


class AppSettingsEnum(Enum):
    MAX_TIME_TO_CHOOSE = "max_time_to_choose"
    TIME_TO_WAIT_BETWEEN = "time_to_wait_between"
    BUTTONS_SIZE = "buttons_size"
    GAZE_PER_SECOND = "gaze_per_second"
