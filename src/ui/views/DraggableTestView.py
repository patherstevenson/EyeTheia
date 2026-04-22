import flet as ft
from ui.AppState import AppState


def DraggableTestView(page: ft.Page, state: AppState):
    widget_list = []




    widget_list.append(ft.Button(content="Go back to main menu", on_click=lambda _: page.push_route("/")))
    return ft.View(
        controls=widget_list,

        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
