import flet as ft
from PIL.ImageOps import expand
from flet.controls import alignment
from torch.nn.modules import container

from ui.AppState import AppState


def ResultScreenView(page: ft.Page, state: AppState):
    page_content = [
        ft.Text(str(res), size=24, weight=ft.FontWeight.W_600)
        for res in state.results
    ]

    page_content.append(
        ft.Button(
            content="Go Back To Main Menu",
            on_click=lambda _: page.run_task(page.push_route, ("/"))
        )
    )

    sf = ft.Column(
        controls=page_content,
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.update()

    return ft.View(
        controls=[sf],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER

    )
