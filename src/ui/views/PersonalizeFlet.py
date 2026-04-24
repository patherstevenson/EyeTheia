from dataclasses import field

import flet as ft
from ui.AppState import AppState


@ft.control
class DragTile(ft.DragTarget):
    def __init__(self, group, word, index, on_swap):
        content = ft.Draggable(
            group=group,
            content=ft.Container(content=ft.Text(word, weight=ft.FontWeight.W_400), width=100, height=100, border=ft.Border.all(2, ft.Colors.BLUE)),
        )
        super().__init__(content)
        self.group = group
        self.word = word
        self.on_accept = on_swap
        self.data = index
        self.expand = True


@ft.control
class WordPicker(ft.Column):
    """A widget to arrange 4 words in a grid"""
    words = []
    index = -1

    def init(self, index=-1, words=["A", "B", "C", "D"]):
        self.expand = True
        self.words = words
        self.build_grid()
        self.index = index

    def build_grid(self):
        self.controls = [
            ft.Row(
                controls=[
                    DragTile(str(self.index), self.words[0], 1, self.handle_swap),
                    DragTile(str(self.index), self.words[1], 2, self.handle_swap),
                ], expand=True
            ),
            ft.Row(
                controls=[
                    DragTile(str(self.index), self.words[2], 3, self.handle_swap),
                    DragTile(str(self.index), self.words[3], 4, self.handle_swap),
                ], expand=True
            )
        ]

    def handle_swap(self, e: ft.DragTargetEvent):
        print(str(e.src.parent.word))

        print(self.words)

        src_index = self.words.index(e.src.parent.word)
        new_index = self.words.index(e.control.word)

        self.words[src_index], self.words[new_index] = self.words[new_index], self.words[src_index]

        # On reconstruit la grille proprement
        self.build_grid()
        self.update()


@ft.control
class GroupCustomization(ft.Row):
    """A widget to configure a single WordGroup"""
    words: list[str] = field(default_factory=list)
    correct_answer: str = ""
    sound: str = ""
    index: int = -1

    def init(self):
        self.words = ["A", "B", "C", "D"]
        self.controls = [
            ft.Checkbox(),

            WordPicker(self.index, self.words)
        ]


def handle_reorder(e: ft.OnReorderEvent):
    rlv = e.control
    moved_item = rlv.controls.pop(e.old_index)  # Remove the reordered item from its old position
    rlv.controls.insert(e.new_index, moved_item)  # Insert the reordered item into its new position
    rlv.update()


def PersonalizeView(page: ft.Page, state: AppState):
    widgets = []

    group_list = [
        ft.Draggable(content=GroupCustomization(index=i), group="group")
        for i in range(20)
    ]

    widgets.append(
        ft.ReorderableListView(
            controls=group_list,
            expand=1,
            auto_scroll=True,
            height=page.height - 100,
            on_reorder=handle_reorder
        )
    )

    widgets.append(ft.VerticalDivider())

    widgets.append(ft.Column(
        controls=[
            ft.Button(content="Go Back to Main Menu",
                      on_click=lambda _: page.run_task(page.push_route, "/WordExperiment")
                      )
        ],
        expand=1
    ))

    return ft.View(
        controls=ft.Row(controls=widgets, expand=True),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
