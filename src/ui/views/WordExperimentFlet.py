import asyncio

import flet as ft
from experiments.wordExperiment.WordExperiment import WordExperiment
from ui.AppState import AppState
from ui.FletUtils import playSound
from utils.config import TEXT_SIZE


@ft.control
class WordExperimentView(ft.View):
    def __init__(self, page: ft.Page, state: AppState, **kwargs):
        super().__init__(**kwargs)

        self.app_scale = 1.5 * TEXT_SIZE

        self.exp = WordExperiment(state, self.get_window_res)

        self.quarter_width = max((page.window.width or 1920) / 2, 200) * state.settings.buttons_size
        self.quarter_height = max((page.window.height or 1080) / 2, 140) * state.settings.buttons_size

        self.container = ft.Column(
            controls=[],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.words = [
            ft.Container(
                content=ft.Button(
                    content=ft.Text(word, size=76 * state.settings.buttons_size * TEXT_SIZE),
                    width=self.quarter_width,
                    height=self.quarter_height,
                    on_click=lambda _, i=index: page.run_task(self.exp.next_words, i)
                ),
                expand=1,
                alignment=ft.Alignment.CENTER,
            )
            for index, word in enumerate(self.exp.word_groups[0].words)
        ]
        self.words_grid = ft.Column(
            controls=[
                ft.Row(
                    controls=self.words[:2],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                ),
                ft.Row(
                    controls=self.words[2:4],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            expand=True,
        )
        self.exp.listeners["show_plus"] = self.show_plus
        self.exp.listeners["show_word_group"] = self.show_word_group

        self.queue = asyncio.Queue()
        self.ui_loop = asyncio.get_running_loop()
        self.process_state = {"process_started": False}

        self.exp.add_listener(self.on_new_coords)

        self.exp.add_finish_listener(self.stop_experiment)

        self.container.controls = [
            ft.Column(
                controls=[
                    ft.Text("Before Starting : ", weight=ft.FontWeight.W_900, size=18 * self.app_scale),
                    ft.Row(
                        controls=[
                            ft.Button(
                                content="Calibration", on_click=state.gaze_manager.calibrate, scale=self.app_scale
                            ),
                            ft.Button(
                                content="Personalize Experiment",
                                on_click=lambda _: page.run_task(page.push_route, "/Personalize"), scale=self.app_scale
                            ),
                            ft.Button(
                                content="Last Results",
                                on_click=lambda _: page.run_task(page.push_route, "/Results"), scale=self.app_scale
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=70 * self.app_scale,
                    ),
                    ft.Button(
                        content="Start Experiment",
                        on_click=self.start_experiment, scale=self.app_scale
                    ),
                    ft.Button(
                        content="Main Menu",
                        on_click=lambda _: page.run_task(self.back_to_main_menu, self.page), scale=self.app_scale
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20 * self.app_scale
            ),
        ]

        self.controls = [self.container]
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

    def get_window_res(self):
        return self.page.window.width, self.page.window.height

    def show_plus(self):
        """Show a big "+" in the middle of the screen for a time set in AppSettings"""
        self.container.controls = [
            ft.Icon(
                icon=ft.Icons.ADD,
                size=100,
                color="black",
            )
        ]
        self.page.update()

    async def show_word_group(self):
        """Show the 4 words of the current word_group in 4 buttons, each one in a quater of the screen, with a size set in AppSettings"""
        current_words = self.exp.get_current_words()

        for word_index, button in enumerate(self.words):
            content = button.content.content
            if content:
                content.value = current_words[word_index]

        self.container.controls = [self.words_grid]
        self.page.update()
        await playSound(self.exp.get_current_sound())

    def on_new_coords(self, cx, cy):
        """Called when the tracker finished to guess the Gaze coordinates"""
        self.ui_loop.call_soon_threadsafe(self.queue.put_nowait, (cx, cy))

    async def start_experiment(self, _):
        """Start an experiment"""
        if not self.process_state["process_started"]:
            self.process_state["process_started"] = True
        await self.exp.start()

    def stop_experiment(self):
        """Stop the running experiment"""
        self.exp.stop()
        self.ui_loop.call_soon_threadsafe(self.queue.put_nowait, None)
        self.process_state["process_started"] = False
        self.page.update()

        self.page.run_task(self.page.push_route, "/Results")

    async def back_to_main_menu(self, page: ft.Page):
        """Go back to main menu"""
        await page.push_route("/")
