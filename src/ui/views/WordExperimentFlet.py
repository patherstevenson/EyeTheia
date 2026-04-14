import GazeManager
import flet as ft
from experiments.WordExperiment import WordExperiment
from flet import controls


# container = ft.Container(
#     # bg_color = ft.Colors.AMBER
# )
def WordExperimentView(gaze_manager: GazeManager):

    exp = WordExperiment(gaze_manager)

    container = [ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100),
                 ft.Button(
                     content="Calibration",
                     on_click=lambda _: print("ouais")
                 )]


    return ft.View(
        controls=
        container

    )
