import flet as ft
from ui.AppState import AppState


def PersonalizeView(page: ft.Page, state: AppState):
    widgets = []

    group_list = []
    #
    # widgets.append(ft.ListView(controls=ft.Column(
    #     controls=group_list,
    #     expand=1,
    #     alignment=ft.MainAxisAlignment.CENTER,
    #     horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    # ),
    #     auto_scroll=True,
    #     height=page.height - 100),
    # )
    #
    widgets.append(ft.VerticalDivider())

    widgets.append(ft.Button(content="Go Back to Main Menu", on_click=lambda _: page.run_task(page.push_route, "/")))

    print("test")

    return ft.View(
        controls=ft.Row(controls=widgets),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
