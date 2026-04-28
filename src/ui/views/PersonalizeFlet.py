from dataclasses import field

import flet as ft
from experiments.wordExperiment.WordGroup import WordGroup
from flet.controls import alignment
from ui.AppState import AppState
from ui.FletUtils import playSound


def PersonalizeView(page: ft.Page, state: AppState):
    """A screen to personalize an experiment"""
    widgets = []

    word_groups = state.word_groups

    group_list = [
        ft.Draggable(
            content=GroupCustomization(
                index=i,
                group=group
            ),
            group=str(i)
        )
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

    widgets.append(
        ft.Column(
            controls=[
                ft.Button(
                    content="Go Back to Main Menu",
                    on_click=lambda _: page.run_task(page.push_route, "/WordExperiment")
                )
            ],
            expand=1
        )
    )

    return ft.View(
        controls=ft.Row(
            controls=widgets,
            expand=True
        ),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

@ft.control
class CorrectAnwserWidget(ft.Dropdown):
    word_group: WordGroup = None

    def init(self):
        self.options = []

        for word in self.word_group.words:
            self.options.append(ft.DropdownOption(key=word, text=word))

        self.value = self.word_group.correct

        self.on_select=self.handle_select

    def handle_select(self, e):
        self.word_group.correct=e.control.value
        print(self.word_group.correct)




@ft.control
class GroupCustomization(ft.Container):
    """A widget to configure a single WordGroup"""
    index: int = -1
    group: WordGroup = None

    def init(self):
        self.border = ft.Border.all(5, ft.Colors.BLACK_26)
        # self.words = ["A", "B", "C", "D"]
        self.content = ft.Row(
            controls=[
                WordPicker(index=self.index, words=self.group.words),
                ft.Column(
                    controls=[
                        SoundPicker(word_group=self.group),
                        CorrectAnwserWidget(word_group=self.group)

                    ]
                )
            ]
        )

    def handle_text_change(self, e):
        self.group.correct = e.control.value



@ft.control
class SoundPicker(ft.Container):
    """A widget to show, play and modify the picked sound of a word_group"""

    page: ft.Page = None
    word_group: WordGroup = None

    def init(self):
        self.content = ft.Row(
            controls=[
                ft.Text(self.word_group.sound),
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    icon_color=ft.Colors.BLUE,
                    icon_size=40,
                    on_click=self.playsound
                )
            ]
        )

    async def playsound(self):
        await playSound(self.word_group.sound)


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
            ft.Row(controls=[DragTile(str(self.index), self.words[0], 0, self.handle_swap, self.handle_change_word), DragTile(str(self.index), self.words[1], 1, self.handle_swap, self.handle_change_word), ], expand=True),
            ft.Row(controls=[DragTile(str(self.index), self.words[2], 2, self.handle_swap, self.handle_change_word), DragTile(str(self.index), self.words[3], 3, self.handle_swap, self.handle_change_word), ], expand=True)]

    def handle_swap(self, e: ft.DragTargetEvent):
        print(str(e.src.parent.word))

        print(self.words)

        src_index = self.words.index(e.src.parent.word)
        new_index = self.words.index(e.control.word)

        self.words[src_index], self.words[new_index] = self.words[new_index], self.words[src_index]

        # On reconstruit la grille proprement
        self.build_grid()
        self.update()
        self.expand=True,

    def handle_change_word(self, e):
        print(str(e.control.value))
        print(str(e.control.parent.parent.parent.index))
        self.words[e.control.parent.parent.parent.index] = e.control.value

        print(str(self.words))


@ft.control
class DragTile(ft.DragTarget):
    def __init__(self, group, word, index, on_swap, on_change):
        content = ft.Draggable(
            expand=True,
            group=group,
            content=ft.Container(
                expand=True,
                content=ft.TextField(value=word, on_change=on_change,expand=True),
                width=100,
                height=100,
                border=ft.Border.all(2, ft.Colors.BLUE),
                alignment=ft.Alignment.CENTER
            ),
        )
        super().__init__(content)
        self.index = index
        self.group = group
        self.word = word
        self.on_accept = on_swap
        self.data = index
        self.expand = True

    def handleChange(self, e):
        new_word = e.control.word


def handle_reorder(e: ft.OnReorderEvent):
    rlv = e.control
    moved_item = rlv.controls.pop(e.old_index)  # Remove the reordered item from its old position
    rlv.controls.insert(e.new_index, moved_item)  # Insert the reordered item into its new position
    rlv.update()
