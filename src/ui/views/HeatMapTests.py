import flet as ft
from ui.AppState import AppState


def HeatMapView(page: ft.Page, state: AppState):


    return ft.View(
        controls=[
            ft.Button(content="Hi !",
                      on_click=lambda _: page.run_task(page.push_route, "/Personalize"))
        ]
    )


