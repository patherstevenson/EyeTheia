import flet as ft
import flet.canvas as cv
from ui.AppState import AppState


@ft.control
class HeatMapView(ft.View):

    def __init__(self, page: ft.Page, state: AppState, **kwargs):
        super().__init__(**kwargs)

        self.built = False

        self.canva = cv.Canvas(expand=True,
                               # width=1920,
                               # height=1080,
                               shapes=[],
                               )

        self.on_size_change = self.handle_resize
        self.show_words: bool = True

        self.index = 0

        self.draw_heatmap(state)

        self.controls = [
            self.canva,
            ft.Row(controls=[
                ft.Button(content="Back To Main Menu",
                          on_click=lambda _: page.run_task(page.push_route, "/Personalize")),
                ft.Button(content="<- Previous Group",
                          on_click=self.previous_group),
                ft.Button(content="Next Group ->",
                          on_click=self.next_group),
            ]),
        ]

    def handle_resize(self, e):
        self.width = e.width
        self.height = e.height
        print("Ca a resize là")
        print(e.control.width)

        if self.built:
            self.canva.height = e.page.window.height * 0.9
            e.control.update()

    def build(self):
        self.built = True

    def draw_heatmap(self, state: AppState = None):
        if state is None:
            state: AppState = self.page.data

        self.canva.shapes.clear()

        if self.show_words:
            # half_width = self.page.window.width / 2
            # half_height = self.page.window.height / 2
            half_width = 860
            half_height = 540

            print(self.width)

            cv.Text(
                x=half_width / 2,
                y=half_height / 2,
                value=state.results[self.index].words.words[0],
            )

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
