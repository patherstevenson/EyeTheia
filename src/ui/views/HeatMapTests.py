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
            paint_heatmap = ft.Paint(
                gradient=ft.PaintRadialGradient(
                    center=(pt.x, pt.y),
                    radius=50,
                    colors=[
                        ft.Colors.with_opacity(0.4, ft.Colors.RED_ACCENT_400),
                        ft.Colors.with_opacity(0.15, ft.Colors.ORANGE_300),
                        # ft.Colors.TRANSPARENT,
                    ],
                    # color_stops=[0.0, 0.5, 1.0]
                )
            )
            canva.shapes.append(
                cv.Circle(
                    pt.x, pt.y, 50, paint=paint_heatmap
                )
            )

        print("a")

        self.controls = [
            canva,
            ft.Button(content="Hi !",
                      on_click=lambda _: page.run_task(page.push_route, "/Personalize"))
        ]
