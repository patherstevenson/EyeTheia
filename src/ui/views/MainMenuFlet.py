import flet as ft
from ui.AppState import AppState


@ft.control
class MoveToButton(ft.Button):
    def __init__(self, direction: str, **kwargs):
        super().__init__(**kwargs)

        self.direction = direction

    def build(self):
        self.on_click = lambda _: self.page.run_task(self.page.push_route, self.direction)


def MainMenuView(page: ft.Page, state: AppState):
    buttons_scale = 1.5

    buttons = [
        ft.Button(
            content="Calibration",
            on_click=state.gaze_manager.calibrate,
            scale=buttons_scale
        ),
        MoveToButton(
            content="Word Experiment",
            direction="/WordExperiment",
            scale=buttons_scale
        ),
        MoveToButton(
            content="FastResults",
            direction="/Results",
            scale=buttons_scale
        ),
        MoveToButton(
            content="Personalize",
            direction="/Personalize",
            scale=buttons_scale
        ),
        MoveToButton(
            content="HeatMap",
            direction="/HeatMap",
            scale=buttons_scale
        ),

    ]

    column = ft.Column(
        controls=buttons,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30
    )

    return ft.View(
        controls=[column],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER
    )
