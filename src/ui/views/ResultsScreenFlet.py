import flet as ft
import flet.canvas as cv
from experiments.wordExperiment.GroupResults import GroupResults
from ui.AppState import AppState
from ui.FletUtils import saveResultsToCSV, loadCSV, playSound
from utils.config import SCREEN_HEIGHT, SCREEN_WIDTH


@ft.control
class ExperiencePreview(ft.Container):
    def __init__(self, res: GroupResults, **kwargs):
        super().__init__(**kwargs)

        self.word_preview = WordPreview(words=res.words.words, size=24, font=ft.FontWeight.W_600, spacing=16)
        self.points_preview = PointsCanva(res)
        # self.score_preview = WordsWidget_old(res.gaze_score, 18, ft.FontWeight.W_600, 8, 4, ft.Colors.BLUE)

        self.content = self.word_preview

        self.state = 0

        self.border = ft.Border.all(6, ft.Colors.BLUE)
        self.expand = 1
        self.aspect_ratio = 1
        self.on_click = self.handle_click

    def handle_click(self, e):
        self.state = self.state % 3
        if self.state == 0:
            self.content = self.points_preview
        elif self.state == 1:
            self.content = self.word_preview

        self.state += 1
        self.update()


@ft.control
class WordPreview(ft.Column):
    def __init__(self, words, size, font: ft.FontWeight, spacing, **kwargs):
        super().__init__(**kwargs)

        self.controls = [ft.Row(
            controls=[ft.Text(words[0], size=size, weight=font),
                      ft.Text(words[1], size=size, weight=font)],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,

        ),
            ft.Row(
                controls=[ft.Text(words[2], size=size, weight=font),
                          ft.Text(words[3], size=size, weight=font)],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            )
        ]
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = spacing
        self.expand = 1
        self.aspect_ratio = 1


@ft.control
class WordsWidget_old(ft.Container):
    """Left part of a word_group widget, with words or points"""

    def __init__(self, data, size, font: ft.FontWeight, spacing, border_width, border_color, is_score: bool = False, **kwargs):
        super().__init__(**kwargs)

        words = []
        for o in data:
            words.append(str(o))

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[ft.Text(words[0], size=size, weight=font),
                              ft.Text(words[1], size=size, weight=font)],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,

                ),
                ft.Row(
                    controls=[ft.Text(words[2], size=size, weight=font),
                              ft.Text(words[3], size=size, weight=font)],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=spacing,
            data=is_score
        )
        self.border = ft.Border.all(border_width, border_color)
        self.expand = 1
        self.aspect_ratio = 1


@ft.control
class DataWidget(ft.Column):
    """Right half of a word_group widget, with the sound, the gaze points and time took to click"""

    def __init__(self, res, page: ft.Page, **kwargs):
        super().__init__(**kwargs)

        self.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(res.words.sound, size=20, weight=ft.FontWeight.W_600),
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW,
                            icon_color=ft.Colors.BLUE,
                            icon_size=40,
                            on_click=lambda _: page.run_task(playSound, res.words.sound)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                ),
                border=ft.Border.all(4, ft.Colors.BLUE_ACCENT),
                expand=1
            )
            ,
            ft.Row(
                controls=[
                    ft.Container(
                        content=WordPreview(res.gaze_score, 18, ft.FontWeight.W_600, 8),
                        border=ft.Border.all(4, ft.Colors.BLUE)
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(str(res.gaze_score[4]) + " gazes failed", size=14, weight=ft.FontWeight.W_600,
                                    overflow=ft.TextOverflow.FADE),
                            ft.Divider(height=9, thickness=3),
                            ft.Text(f"{round(res.total_time, 2)} seconds to choose", size=14, weight=ft.FontWeight.W_600,
                                    overflow=ft.TextOverflow.FADE),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    )

                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=1
            )
        ]
        self.expand = 1
        self.aspect_ratio = 1


def switch_infos(word_tab_widget: ft.Control, res: GroupResults, page):
    """Switch the main tab between the 4 words and a visualization of where the user looked"""
    if word_tab_widget.content.data:
        word_tab_widget.content = WordsWidget_old(res.words.words, 24, ft.FontWeight.W_600, 16, 6, ft.Colors.BLUE, False).content
        page.update()
    else:
        word_tab_widget.content = PointsCanva(page, res)
        page.update()

    word_tab_widget.on_click = lambda _: switch_infos(word_tab_widget, res, page)


@ft.control
class ResWidget(ft.Container):
    """Widget used to show results of a single word_group"""

    def __init__(self, page: ft.Page, res: GroupResults, **kwargs):
        super().__init__(**kwargs)

        # word_tab_widget = WordsWidget_old(res.words.words, 24, ft.FontWeight.W_600, 16, 6, ft.Colors.BLUE)
        word_tab_widget = ExperiencePreview(res)

        word_tab_widget.aspect_ratio = 1
        word_tab_widget.ink = True

        # word_tab_widget.on_click = lambda _: switch_infos(word_tab_widget, res, page)

        res_data_widget = DataWidget(res, page)

        self.content = ft.Row(
            controls=[
                # TabWidget : Words
                word_tab_widget,
                ft.VerticalDivider(width=9, thickness=3),
                res_data_widget
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER, expand_loose=True,
            spacing=50,
        )
        self.border = ft.Border.all(10, ft.Colors.BLUE_ACCENT)
        self.expand = 1
        self.margin = ft.Margin.symmetric(horizontal=20)


@ft.control
class PointsCanva(ft.Container):
    def __init__(self, res: GroupResults, **kwargs):
        super().__init__(**kwargs)

        self.res = res
        self.built = False

        self.canva = cv.Canvas(
            on_resize=self.handle_resize
        )

        self.content = self.canva
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

            old_x = -1
            old_y = -1

            style = ft.TextStyle(size=10)

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
class ResultScreenView(ft.View):
    """Returns a view to show all the results of an experiment"""

    def __init__(self, page: ft.Page, state: AppState, **kwargs):
        super().__init__(**kwargs)
        widget_list = [
            ResWidget(page, res)
            for res in state.results
        ]

        page.update()

        height = page.height

        if height is None:
            height = 0

        self.controls = [
            ft.ListView(controls=[ft.Column(
                controls=widget_list,
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )],
                auto_scroll=True,
                height=height - 100, ),
            ft.Row(controls=[
                ft.Button(
                    content="Go Back To Main Menu",
                    on_click=lambda _: page.run_task(page.push_route, "/")
                ),
                ft.Button(
                    content="Save to CSV",
                    on_click=lambda _: page.run_task(saveResultsToCSV, state)
                ),
                ft.Button(
                    content="Load CSV",
                    on_click=lambda _: page.run_task(loadCSV, page)
                ),

            ]),
        ]
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
