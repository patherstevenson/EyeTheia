import flet as ft
from ui.AppState import AppState


async def onWordExperiment(page: ft.Page):
    """Show WordExperiment View"""
    await page.push_route("/WordExperiment")


def MainMenuView(page: ft.Page, state: AppState):
    buttons = [
        ft.Button(
            content="Calibration",
            on_click=state.gaze_manager.calibrate
        ),
        ft.Button(
            content="Word Experience",
            on_click=lambda _: page.run_task(onWordExperiment, page)
        ),
        ft.Button(
            content="FastResults",
            on_click=lambda _: page.run_task(page.push_route, "/Results")
        ),
        ft.Button(
            content="Personalize",
            on_click=lambda _: page.run_task(page.push_route, "/Personalize")
        ),
    ]
    column = ft.Column(
        controls=buttons,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    return ft.View(
        controls=[column],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER
    )
