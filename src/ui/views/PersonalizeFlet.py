import flet as ft

from experiments.wordExperiment.WordGroup import WordGroup
from ui.AppState import AppState
from ui.FletUtils import playSound

WORDS_PER_GROUP = 4


def PersonalizeView(page: ft.Page, state: AppState):
    """Build the screen used to customize word groups."""
    group_list = [
        GroupCustomization(group_index=index, word_group=group)
        for index, group in enumerate(state.word_groups)
    ]

    reorderable_list = ft.ReorderableListView(
        show_default_drag_handles=False,
        controls=group_list,
        expand=1,
        auto_scroll=True,
        height=page.height - 100,
        on_reorder=lambda e: handle_reorder(e, state),
        spacing=120,
    )

    return ft.View(
        controls=[
            ft.Row(
                controls=[
                    reorderable_list,
                    ft.VerticalDivider(),
                    ft.Column(
                        controls=[
                            ft.Button(
                                content="Go Back to Main Menu",
                                on_click=lambda _: page.run_task(page.push_route, "/WordExperiment"),
                            )
                        ],
                        expand=1,
                    ),
                ],
                expand=True,
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )


@ft.control
class CorrectAnswerDropdown(ft.Dropdown):
    word_group: WordGroup = None

    def init(self):
        self.options = [
            ft.DropdownOption(key=word, text=word)
            for word in self.word_group.words
        ]
        self.value = self.word_group.correct
        self.on_select = self.handle_select

    def handle_select(self, e):
        self.word_group.correct = e.control.value


@ft.control
class SoundPicker(ft.Container):
    """Display the selected sound and allow replaying it."""

    word_group: WordGroup = None

    def init(self):
        self.content = ft.Row(
            controls=[
                ft.Text(self.word_group.sound),
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    icon_color=ft.Colors.BLUE,
                    icon_size=40,
                    on_click=self.play_sound,
                ),
            ]
        )
        self.border = ft.Border.all(2, ft.Colors.GREY)

    async def play_sound(self, _):
        await playSound(self.word_group.sound)


@ft.control
class GroupCustomization(ft.Container):
    """Widget used to edit one WordGroup."""

    group_index: int = -1
    word_group: WordGroup = None

    def init(self):
        self.expand = True
        self.padding = 10
        self.border = ft.Border.all(5, ft.Colors.BLACK_26)
        self.content = ft.Row(
            controls=[
                WordPicker(word_group=self.word_group),
                ft.Column(
                    controls=[
                        SoundPicker(word_group=self.word_group),
                        CorrectAnswerDropdown(word_group=self.word_group),
                    ]
                ),
                ft.ReorderableDragHandle(
                    content=ft.Icon(ft.Icons.DRAG_INDICATOR, color=ft.Colors.BLUE),
                    expand=1,
                ),
            ],
            expand=1,
        )


@ft.control
class WordPicker(ft.Column):
    """Display a 2x2 editable grid for one WordGroup."""

    word_group: WordGroup = None

    def init(self):
        self.expand = True
        self.validate_words()
        self.build_grid()

    def validate_words(self):
        if len(self.word_group.words) != WORDS_PER_GROUP:
            raise ValueError(
                f"Each WordGroup must contain exactly {WORDS_PER_GROUP} words. "
                f"Received {len(self.word_group.words)}."
            )

    def build_grid(self):
        words = self.word_group.words
        self.controls = [
            ft.Row(
                controls=[
                    DragTile(words[0], 0, self.handle_swap, self.handle_change_word),
                    DragTile(words[1], 1, self.handle_swap, self.handle_change_word),
                ],
                expand=True,
            ),
            ft.Row(
                controls=[
                    DragTile(words[2], 2, self.handle_swap, self.handle_change_word),
                    DragTile(words[3], 3, self.handle_swap, self.handle_change_word),
                ],
                expand=True,
            ),
        ]

    def handle_swap(self, e: ft.DragTargetEvent):
        source_index = e.src.data
        target_index = e.control.data
        words = self.word_group.words

        words[source_index], words[target_index] = words[target_index], words[source_index]
        self.build_grid()
        self.update()

    def handle_change_word(self, word_index: int, new_word: str):
        self.word_group.words[word_index] = new_word


@ft.control
class DragTile(ft.DragTarget):
    def __init__(self, word: str, index: int, on_swap, on_change):
        text_field = ft.TextField(
            value=word,
            on_change=lambda e, tile_index=index: on_change(tile_index, e.control.value),
            expand=True,
        )

        content = ft.Draggable(
            expand=True,
            content=ft.Container(
                expand=True,
                content=text_field,
                width=100,
                height=100,
                alignment=ft.Alignment.CENTER,
            ),
            data=index,
        )

        super().__init__(content=content, on_accept=on_swap, data=index, expand=True)


def handle_reorder(e: ft.OnReorderEvent, state: AppState):
    word_groups = list(state.word_groups)
    moved_group = word_groups.pop(e.old_index)
    word_groups.insert(e.new_index, moved_group)
    state.set_word_groups(word_groups)

    reordered_controls = list(e.control.controls)
    moved_control = reordered_controls.pop(e.old_index)
    reordered_controls.insert(e.new_index, moved_control)

    for index, control in enumerate(reordered_controls):
        control.group_index = index

    e.control.controls = reordered_controls
    e.control.update()
