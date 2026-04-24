from dataclasses import field

import flet as ft
from ui.AppState import AppState


@ft.control
class DragTile(ft.DragTarget):
    def __init__(self, group, word, index, on_swap):
        content = ft.Draggable(
            group=group,
            content=ft.Container(content=ft.TextField(value=word), width=100, height=100, border=ft.Border.all(2, ft.Colors.BLUE)),
        )
        super().__init__(content)
        self.group = group
        self.word = word
        self.on_accept = on_swap
        self.data = index
        self.expand = True

    def handleChange(self, e):
        new_word = e.control.word



@ft.control
class WordPicker(ft.Column):
    """A widget to arrange 4 words in a grid"""
    words: list[str] = field(default_factory=list)
    index: int = -1

    def init(self):
        self.expand = True
        self.build_grid()

    def build_grid(self):
        self.controls = [
            ft.Row(
                controls=[
                    DragTile(str(self.index), self.words[0], 0, self.handle_swap),
                    DragTile(str(self.index), self.words[1], 1, self.handle_swap),
                ], expand=True
            ),
            ft.Row(
                controls=[
                    DragTile(str(self.index), self.words[2], 2, self.handle_swap),
                    DragTile(str(self.index), self.words[3], 3, self.handle_swap),
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
class GroupCustomization(ft.Container):
    """A widget to configure a single WordGroup"""
    words: list[str] = field(default_factory=list)
    correct_answer: str = ""
    sound: str = ""
    index: int = -1

    def init(self):
        self.border = ft.Border.all(5, ft.Colors.BLACK_26)
        # self.words = ["A", "B", "C", "D"]
        self.content = ft.Row(controls=[


            ft.Checkbox(),

            WordPicker(index = self.index, words = self.words)
        ])


def handle_reorder(e: ft.OnReorderEvent):
    rlv = e.control
    moved_item = rlv.controls.pop(e.old_index)  # Remove the reordered item from its old position
    rlv.controls.insert(e.new_index, moved_item)  # Insert the reordered item into its new position
    rlv.update()


def PersonalizeView(page: ft.Page, state: AppState):
    widgets = []

    word_groups = state.word_groups

    group_list = [
        ft.Draggable(content=GroupCustomization(index=i, words = group.words, correct_answer=group.correct, sound=group.sound,), group=str(i))
        for i, group in enumerate(word_groups)
    ]

    widgets.append(
        ft.ReorderableListView(
            controls=group_list,
            expand=1,
            auto_scroll=True,
            height=page.height - 100,
            on_reorder=handle_reorder,
            spacing=120
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
