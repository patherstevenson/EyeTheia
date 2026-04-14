import asyncio
import threading

import flet as ft
import mediapipe as mp

from GazeManager import GazeManager
from experiments.WordExperiment import WordExperiment


def WordExperimentView(page: ft.Page, gaze_manager: GazeManager):
    exp = WordExperiment(gaze_manager)
    cx_text = ft.Text("cx: -")
    cy_text = ft.Text("cy: -")
    status_text = ft.Text("Status: idle")

    state = {"running": False}
    queue = asyncio.Queue()

    def produce_gaze(loop: asyncio.AbstractEventLoop):
        with mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1) as face_mesh:
            while state["running"]:
                cx, cy = exp.gaze_manager.getGazeCoords(face_mesh)
                loop.call_soon_threadsafe(queue.put_nowait, (cx, cy))

    async def process_gaze():
        while True:
            coords = await queue.get()
            if coords is None:
                break
            cx, cy = coords
            cx_text.value = f"cx: {cx}"
            cy_text.value = f"cy: {cy}"
            page.update()

    async def start_experiment(_):
        if state["running"]:
            return
        state["running"] = True
        status_text.value = "Statut: running"
        page.update()

        loop = asyncio.get_running_loop()
        worker = threading.Thread(target=produce_gaze, args=(loop,), daemon=True)
        worker.start()
        page.run_task(process_gaze)

    def stop_experiment(_):
        state["running"] = False
        status_text.value = "Statut: stopped"
        queue.put_nowait(None)
        page.update()

    return ft.View(
        controls=[
            status_text,
            cx_text,
            cy_text,
            ft.Row(
                controls=[
                    ft.Button(
                        content="Demarrer l'experience",
                        on_click=start_experiment,
                    ),
                    ft.Button(
                        content="Stop",
                        on_click=stop_experiment,
                    ),
                ]
            ),
        ]
    )
