import flet as ft
import flet.canvas as cv
from fontTools.cffLib import width
from setuptools.config import expand
from ui.AppState import AppState


def CanvaTestView(page: ft.Page, state: AppState):
    canva = cv.Canvas(
        width=200,
        height=200,
        expand=True,
        shapes=[
            cv.Text(x=100, y=100, value="100,100", style=ft.TextStyle(size=10), alignment=ft.Alignment.CENTER, ),
            cv.Text(x=100, y=200, value="100,200", style=ft.TextStyle(size=10), alignment=ft.Alignment.CENTER, ),
            cv.Text(x=200, y=100, value="200,100", style=ft.TextStyle(size=10), alignment=ft.Alignment.CENTER, ),
            cv.Text(x=200, y=200, value="200,200", style=ft.TextStyle(size=10), alignment=ft.Alignment.CENTER, ),
            cv.Line(x1=0 , y1=0,  x2=200,  y2=200, paint=ft.Paint(stroke_width=2, style=ft.PaintingStyle.STROKE))
        ]
    )

    return ft.View(
        controls=canva,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )
