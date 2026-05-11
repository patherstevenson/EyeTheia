import flet as ft
from ui import AppState
from ui.FletUtils import load_this_csv


def HeatMapView(page: ft.Page, state: AppState):


    return ft.View(
        controls=[
            ft.Button(content="Hi !",
                      on_click=lambda _: page.run_task(page.push_route, "/Personalize"))
        ]
    )


