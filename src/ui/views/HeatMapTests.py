import flet as ft
import flet.canvas as cv
from ui.AppState import AppState


@ft.control
class HeatMapView(ft.View):

    def __init__(self, page: ft.Page, state: AppState, **kwargs):
        super().__init__(**kwargs)

        canva = cv.Canvas(expand=True,
                          shapes=[]
                          )

        for pt in state.results[0].gaze_points:
            canva.shapes.append(
                cv.Circle(
                    pt.x, pt.y, 20, paint=ft.Paint(color=ft.Colors.BLUE.with_opacity(0.4, ft.Colors.RED))
                )
            )

        print("a")

        self.controls = [
            canva,
            ft.Button(content="Hi !",
                      on_click=lambda _: page.run_task(page.push_route, "/Personalize"))
        ]

    #
    # def handle_resize(self, e):
    #     """Handle when the window resize to update all widgets"""
    #     canva_width: float = e.width
    #     canva_height: float = e.height
    #
    #
    #     (res, page) = e.control.data
    #     shapes = []
    #
    #     old_x = -1
    #     old_y = -1
    #
    #     style = ft.TextStyle(size=10)
    #
    #     for pt in res.gaze_points:
    #         stroke_paint = ft.Paint(stroke_width=2, style=ft.PaintingStyle.STROKE, color=ft.Colors.BLACK)
    #
    #         x = round((pt.x / SCREEN_WIDTH) * canva_width)
    #         y = round((pt.y / SCREEN_HEIGHT) * canva_height)
    #         shapes.append(cv.Circle(x=x, y=y, radius=10, paint=stroke_paint))
    #         shapes.append(cv.Text(x=x, y=y, value=str(pt.index), style=style, alignment=ft.Alignment.CENTER))
    #         if old_x >= 0 & old_y >= 0:
    #             shapes.append(cv.Line(paint=stroke_paint, x1=old_x, y1=old_y, x2=x, y2=y))
    #         old_x = x
    #         old_y = y
    #
    #     e.control.shapes = shapes
    #
    #
    #     page.update()
