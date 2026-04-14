import flet as ft
from experiments.WordExperiment import WordExperiment
from flet import controls

# container = ft.Container(
#     # bg_color = ft.Colors.AMBER
# )



container = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)



def WordExperimentView():
    return ft.View(
        controls=[
            container
        ]
    )