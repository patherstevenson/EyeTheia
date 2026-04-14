import asyncio

import GazeManager
import flet as ft
from experiments import WordGroup
from experiments.WordExperiment import WordExperiment


def WordExperimentView(page: ft.Page, gaze_manager: GazeManager, word_groups: [WordGroup]):
    exp = WordExperiment(gaze_manager, word_groups)
    cx_text = ft.Text("cx: -")
    cy_text = ft.Text("cy: -")

    container = ft.Column(controls=[])

    words = [
        ft.Button(
            content=ft.Text(word),
            on_click=lambda _, i=index: choose(i)
        )
        for index, word in enumerate(word_groups[0].words)
    ]

    def setWordGroup(group_index):
        for word_index, button in enumerate(words):
            button.content.value = word_groups[group_index].words[word_index]

    def choose(index):
        exp.choose(index)
        setWordGroup(exp.actual_group_index)
        page.update()

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
        container.controls = words
        page.update()

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
        controls=container
    )
