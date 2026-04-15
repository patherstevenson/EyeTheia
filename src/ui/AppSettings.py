from dataclasses import dataclass


@dataclass
class WordExperimentSettings:
    max_time_to_choose: int = 10
    time_to_wait_between: float = 1.0
    buttons_size: float = 1.0
