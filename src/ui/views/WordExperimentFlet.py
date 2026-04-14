import asyncio


from playsound3 import playsound
import GazeManager
import flet as ft
from experiments import WordGroup
from experiments.WordExperiment import WordExperiment


def WordExperimentView(page: ft.Page, gaze_manager: GazeManager, word_groups: [WordGroup]):
    exp = WordExperiment(gaze_manager, word_groups)
    cx_text = ft.Text("cx: -")
    cy_text = ft.Text("cy: -")
    quarter_width = max((page.window.width or 1200) / 2 - 24, 200)
    quarter_height = max((page.window.height or 800) / 2 - 24, 140)

    container = ft.Column(
        controls=[],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    words = [
        ft.Button(
            content=ft.Text(word),
            width=quarter_width,
            height=quarter_height,
            on_click=lambda _, i=index: page.run_task(choose, i)
        )
        for index, word in enumerate(word_groups[0].words)
    ]

    words_grid = ft.Column(
        controls=[
            ft.Row(
                controls=words[:2],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=words[2:4],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
    )

    def set_word_group(group_index):
        for word_index, button in enumerate(words):
            button.content.value = word_groups[group_index].words[word_index]

    def show_word_group(group_index):
        set_word_group(group_index)
        container.controls = [words_grid]
        playsound("src/experiments/res/sounds/" + word_groups[exp.actual_index].sound)
        page.update()

    async def choose(index):
        exp.choose(index)

        container.controls = [
            ft.Icon(
                icon=ft.Icons.ADD,
                size=100,
                color="black",
            )
        ]
        page.update()

        await asyncio.sleep(3)

        if exp.actual_index < len(word_groups):
            show_word_group(exp.actual_index)

    queue = asyncio.Queue()
    ui_loop = asyncio.get_running_loop()
    state = {"process_started": False}

    def on_new_coords(cx, cy):
        ui_loop.call_soon_threadsafe(queue.put_nowait, (cx, cy))

    exp.add_listener(on_new_coords)

    async def process_results():
        while True:
            coords = await queue.get()
            if coords is None:
                break
            cx, cy = coords
            cx_text.value = f"cx: {cx}"
            cy_text.value = f"cy: {cy}"
            page.update()

    async def start_experiment(_):
        if not state["process_started"]:
            state["process_started"] = True
            page.run_task(process_results)
        exp.start()
        show_word_group(exp.actual_index)

    def stop_experiment(_):
        exp.stop()
        ui_loop.call_soon_threadsafe(queue.put_nowait, None)
        state["process_started"] = False
        page.update()

    async def back_to_main_menu(page: ft.Page):
        await page.push_route("/")

    container.controls = [
        ft.Row(
            controls=[
                ft.Button(
                    content="Démarrer l'expérience",
                    on_click=start_experiment,
                ),
                ft.Button(
                    content="Stop",
                    on_click=stop_experiment,
                ),
            ]
        ),
        ft.Row(
            controls=[
                ft.Button(
                    content="MainMenu",
                    on_click=lambda _: page.run_task(back_to_main_menu, page)
                )
            ]
        ),
    ]

    return ft.View(
        controls=[container],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )
