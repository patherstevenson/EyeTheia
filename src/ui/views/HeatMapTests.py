import flet as ft
import flet.canvas as cv
from ui.AppState import AppState


@ft.control
class HeatMapView(ft.View):

    def __init__(self, page: ft.Page, state: AppState, **kwargs):
        super().__init__(**kwargs)

        self.canva = cv.Canvas(expand=True,
                               shapes=[]
                               )

        self.index = 0

        self.draw_heatmap(state)

        self.controls = [
            self.canva,
            ft.Button(content="Hi !",
                      on_click=lambda _: page.run_task(page.push_route, "/Personalize")),
            ft.Button(content="Next Group",
                      on_click=self.next_group),
            ft.Button(content="Previous Group",
                      on_click=self.previous_group),
        ]

    def draw_heatmap(self, state: AppState = None):
        if state is None:
            state = self.page.data

        self.canva.shapes.clear()
        for pt in state.results[self.index].gaze_points:
            paint_heatmap = ft.Paint(
                gradient=ft.PaintRadialGradient(
                    center=(pt.x, pt.y),
                    radius=50,
                    colors=[
                        ft.Colors.with_opacity(0.4, ft.Colors.RED_ACCENT_400),
                        ft.Colors.with_opacity(0.2, ft.Colors.ORANGE_300),
                        ft.Colors.with_opacity(0.0, ft.Colors.ORANGE),
                        # ft.Colors.TRANSPARENT,
                    ],
                    color_stops=[0.0, 0.5, 1.0]
                )
            )
            self.canva.shapes.append(
                cv.Circle(
                    pt.x, pt.y, 50, paint=paint_heatmap
                )
            )

    def next_group(self):
        state: AppState = self.page.data
        if self.index < len(state.results) - 2:
            self.index += 1
            self.draw_heatmap()
            self.update()


    def previous_group(self):
        state: AppState = self.page.data
        if self.index > 0:
            self.index -= 1
            self.draw_heatmap()
            self.update()
