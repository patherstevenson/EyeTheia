import flet as ft
import flet.canvas as cv
from experiments.wordExperiment.GroupResults import GroupResults
from ui.AppState import AppState
from ui.FletUtils import saveResultsToCSV, loadCSV, playSound
from utils.config import SCREEN_HEIGHT, SCREEN_WIDTH, TEXT_SIZE


@ft.control
class ExperiencePreview(ft.Container):
    def __init__(self, init_preview, **kwargs):
        super().__init__(**kwargs)

        self.content = init_preview

        self.border = ft.Border.all(6, ft.Colors.BLUE)
        self.expand = 1
        self.aspect_ratio = 1
        self.ink = True


@ft.control
class TrajectoriesPreview(cv.Canvas):
    def __init__(self, res: GroupResults, **kwargs):
        super().__init__(**kwargs)

        self.res = res
        self.built = False

        self.on_resize = self.handle_resize

        self.expand = 1
        self.aspect_ratio = 16 / 9
        self.data = True

    def build(self):
        self.built = True

    def handle_resize(self, e):
        """Handle when the window resize to update all widgets"""
        canva_width: float = e.width
        canva_height: float = e.height

        if self.built:
            page = self.page

            shapes = []

            shapes.extend(words_in_canva(res=self.res, canva_width=canva_width, canva_height=canva_height))

            old_x = -1
            old_y = -1

            style = ft.TextStyle(size=10 * TEXT_SIZE)

            for pt in self.res.gaze_points:
                # stroke_paint = ft.Paint(stroke_width=2, style=ft.PaintingStyle.STROKE, color=ft.Colors.random(exclude=[ft.Colors.WHITE, ft.Colors.GREY]))
                stroke_paint = ft.Paint(stroke_width=2, style=ft.PaintingStyle.STROKE, color=ft.Colors.BLACK)

                x = round((pt.x / SCREEN_WIDTH) * canva_width)
                y = round((pt.y / SCREEN_HEIGHT) * canva_height)
                shapes.append(cv.Circle(x=x, y=y, radius=10, paint=stroke_paint))
                shapes.append(cv.Text(x=x, y=y, value=str(pt.index), style=style, alignment=ft.Alignment.CENTER))
                if old_x >= 0 & old_y >= 0:
                    shapes.append(cv.Line(paint=stroke_paint, x1=old_x, y1=old_y, x2=x, y2=y))
                old_x = x
                old_y = y

            e.control.shapes = shapes

            page.update()


@ft.control
class HeatMap(cv.Canvas):
    def __init__(self, res: GroupResults, **kwargs):
        super().__init__(**kwargs)

        self.res = res
        self.shapes = []

        self.canva_width = 1920
        self.canva_height = 1080

        self.on_resize = self.handle_resize

    def handle_resize(self, e):
        """Handle when the window resize to update all widgets"""
        self.canva_width: float = e.width
        self.canva_height: float = e.height
        self.draw_heatmap()

    def draw_heatmap(self):
        self.shapes.clear()

        self.shapes.extend(words_in_canva(res=self.res, canva_width=self.canva_width, canva_height=self.canva_height))

        for pt in self.res.gaze_points:
            x = round((pt.x / SCREEN_WIDTH) * self.canva_width)
            y = round((pt.y / SCREEN_HEIGHT) * self.canva_height)

            paint_heatmap = ft.Paint(
                gradient=ft.PaintRadialGradient(
                    center=(x, y),
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
            self.shapes.append(
                cv.Circle(
                    x, y, 50, paint=paint_heatmap
                )
            )


def words_in_canva(res, canva_width, canva_height):
    shapes = []

    quarter_width = round(canva_width / 4)
    quarter_height = round(canva_height / 4)

    text_style = ft.TextStyle(size=50 * TEXT_SIZE)

    shapes.append(cv.Text(value=res.word_group.words[0], x=quarter_width, y=quarter_height, alignment=ft.Alignment.CENTER, style=text_style))
    shapes.append(cv.Text(value=res.word_group.words[1], x=quarter_width * 3, y=quarter_height, alignment=ft.Alignment.CENTER, style=text_style))
    shapes.append(cv.Text(value=res.word_group.words[2], x=quarter_width, y=quarter_height * 3, alignment=ft.Alignment.CENTER, style=text_style))
    shapes.append(cv.Text(value=res.word_group.words[3], x=quarter_width * 3, y=quarter_height * 3, alignment=ft.Alignment.CENTER, style=text_style))

    return shapes


@ft.control
class WordPreview(cv.Canvas):
    """Preview of words with scores (numerals and circles)"""

    def __init__(self, res: GroupResults, **kwargs):
        super().__init__(**kwargs)

        self.res = res

        self.shapes = []

        self.canva_width = SCREEN_WIDTH
        self.canva_height = SCREEN_HEIGHT

        self.on_resize = self.handle_resize

    def handle_resize(self, e):
        """Handle when the window resize to update all widgets"""
        self.canva_width: float = e.width
        self.canva_height: float = e.height
        self.draw_canva()

    def draw_canva(self):
        self.shapes = []
        self.shapes.extend(words_in_canva(res=self.res, canva_width=self.canva_width, canva_height=self.canva_height))

        quarter_width = round(self.canva_width / 4)
        quarter_height = round(self.canva_height / 4)

        total_score = 0
        for score in self.res.gaze_score:
            total_score += score

        if total_score > 0:
            stroke_paint = ft.Paint(stroke_width=2, style=ft.PaintingStyle.STROKE, color=ft.Colors.BLACK)

            max_radius = min(quarter_width, quarter_height)
            self.shapes.append(cv.Circle(x=quarter_width, y=quarter_height, radius=max_radius * (self.res.gaze_score[0] / total_score), paint=stroke_paint))
            self.shapes.append(cv.Circle(x=quarter_width * 3, y=quarter_height, radius=max_radius * (self.res.gaze_score[1] / total_score), paint=stroke_paint))
            self.shapes.append(cv.Circle(x=quarter_width, y=(quarter_height * 3), radius=max_radius * (self.res.gaze_score[2] / total_score), paint=stroke_paint))
            self.shapes.append(cv.Circle(x=quarter_width * 3, y=(quarter_height * 3), radius=max_radius * (self.res.gaze_score[3] / total_score), paint=stroke_paint))

        distance_above_text = self.canva_height / 20
        self.shapes.append(cv.Text(alignment=ft.Alignment.CENTER, x=quarter_width, y=quarter_height - distance_above_text, value=str(self.res.gaze_score[0])))
        self.shapes.append(cv.Text(alignment=ft.Alignment.CENTER, x=quarter_width * 3, y=quarter_height - distance_above_text, value=str(self.res.gaze_score[1])))
        self.shapes.append(cv.Text(alignment=ft.Alignment.CENTER, x=quarter_width, y=(quarter_height * 3) - distance_above_text, value=str(self.res.gaze_score[2])))
        self.shapes.append(cv.Text(alignment=ft.Alignment.CENTER, x=quarter_width * 3, y=(quarter_height * 3) - distance_above_text, value=str(self.res.gaze_score[3])))


@ft.control
class PlaySoundWidget(ft.Container):
    def __init__(self, res, page, **kwargs):
        super().__init__(**kwargs)

        self.content = ft.Row(
            controls=[
                ft.Text(res.word_group.sound, size=20 * TEXT_SIZE, weight=ft.FontWeight.W_600),
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    icon_color=ft.Colors.BLUE,
                    icon_size=40,
                    on_click=lambda _: page.run_task(playSound, res.word_group.sound)
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
        self.border = ft.Border.all(4, ft.Colors.BLUE_ACCENT)
        self.border_radius = ft.BorderRadius.all(15)
        self.expand = 1


@ft.control
class DataWidget(ft.Column):
    """Right half of a word_group widget, with the sound, the gaze points and time took to click"""

    def __init__(self, res: GroupResults, page: ft.Page, init_previews, **kwargs):
        super().__init__(**kwargs)

        (secondary_preview, third_preview) = init_previews

        style = ft.TextStyle(size=14 * TEXT_SIZE, weight=ft.FontWeight.W_600, overflow=ft.TextOverflow.FADE)

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        PlaySoundWidget(res, page),
                        ft.Row(
                            controls=[
                                ft.TextField(label="Gaze failed", value=str(res.gaze_score[4]), text_style=style, read_only=True, width=150),
                                ft.VerticalDivider(width=9, thickness=3),
                                ft.TextField(label="Time to Choose", value=f"{round(res.total_time, 2)} seconds", text_style=style, read_only=True, width=150),
                                ft.VerticalDivider(width=9, thickness=3),
                                ft.TextField(label="Window Resolution", value=f"{res.screen_width} - {res.screen_height}", text_style=style, read_only=True, width=150),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                            expand=1
                        )
                    ]
                ),
                expand=True
            ),
            ft.Row(
                controls=[
                    secondary_preview,
                    third_preview,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=1
            )
        ]
        self.expand = 1
        self.aspect_ratio = 1


@ft.control
class WordGroupResWidget(ft.Container):
    """Widget used to show results of a single word_group"""

    def __init__(self, page: ft.Page, res: GroupResults, **kwargs):
        super().__init__(**kwargs)

        self.word_preview = WordPreview(res=res)
        self.trajectories_preview = TrajectoriesPreview(res)
        self.heatmap = HeatMap(res)

        self.main_preview = ExperiencePreview(on_click=self.handle_click, init_preview=self.word_preview)
        self.second_preview = ExperiencePreview(on_click=self.handle_click, init_preview=self.trajectories_preview)
        self.third_preview = ExperiencePreview(on_click=self.handle_click, init_preview=self.heatmap)

        self.state = 0

        res_data_widget = DataWidget(res, page, init_previews=(self.second_preview, self.third_preview))

        self.content = ft.Row(
            controls=[
                # TabWidget : Words
                self.main_preview,
                ft.VerticalDivider(),
                res_data_widget
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER, expand_loose=True,
            spacing=50,
        )
        self.border = ft.Border.all(10, ft.Colors.BLUE_ACCENT)
        self.border_radius = ft.BorderRadius.all(5)
        self.expand = 1
        self.margin = ft.Margin.symmetric(horizontal=20, vertical=5)
        self.padding = ft.Padding.all(5)

    def handle_click(self, e):
        self.state += 1
        self.state = self.state % 3
        if self.state == 0:
            self.main_preview.content = self.word_preview
            self.second_preview.content = self.trajectories_preview
            self.third_preview.content = self.heatmap
        elif self.state == 1:
            self.main_preview.content = self.trajectories_preview
            self.second_preview.content = self.heatmap
            self.third_preview.content = self.word_preview
        elif self.state == 2:
            self.main_preview.content = self.heatmap
            self.second_preview.content = self.word_preview
            self.third_preview.content = self.trajectories_preview

        self.update()
        self.main_preview.update()
        self.second_preview.update()
        self.third_preview.update()


def handle_size_change(e):
    e.control.height = e.page.window.height - 100
    e.control.update()


@ft.control
class ResultScreenView(ft.View):
    """Returns a view to show all the results of an experiment"""

    def __init__(self, page: ft.Page, state: AppState, **kwargs):
        super().__init__(**kwargs)
        widget_list = [
            WordGroupResWidget(page, res)
            for res in state.results
        ]

        page.update()

        height = page.height

        if height is None:
            height = 0

        self.controls = [
            ft.ListView(
                controls=widget_list,
                expand=True,
                on_size_change=lambda e: handle_size_change(e),
                auto_scroll=True,
                height=height - 100, ),
            ft.Row(controls=[
                ft.Button(
                    content="Go Back To Main Menu",
                    on_click=lambda _: page.run_task(page.push_route, "/"),
                    scale=TEXT_SIZE
                ),
                ft.Button(
                    content="Save to CSV",
                    on_click=lambda _: page.run_task(saveResultsToCSV, state),
                    scale=TEXT_SIZE
                ),
                ft.Button(
                    content="Load CSV",
                    on_click=lambda _: page.run_task(loadCSV, page),
                    scale=TEXT_SIZE
                ),

            ]),
        ]
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
