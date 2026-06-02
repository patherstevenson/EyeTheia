from typing import Callable
import asyncio

import flet as ft
from experiments.wordExperiment.WordGroup import WordGroup
from ui.AppSettings import AppSettingsEnum
from ui.AppState import AppState
from ui.FletUtils import playSound, loadCSV, saveExperimentToCSV
from utils.config import TEXT_SIZE

WORDS_PER_GROUP = 4


@ft.control
class PersonalizeView(ft.View):
    """Build the screen used to customize word groups."""

    def handle_size_change(self, e):
        e.control.height = e.page.window.height
        e.control.update()

    def handle_reorder(self, e: ft.OnReorderEvent, app_state: AppState, update_callback):
        if e.old_index is None:
            old_index = -1
        else:
            old_index = e.old_index
        if e.new_index is None:
            new_index = -1
        else:
            new_index = e.new_index
        moved_group = app_state.word_groups.pop(old_index)
        app_state.word_groups.insert(new_index, moved_group)

        update_callback()

    def __init__(self, page: ft.Page, state: AppState, **kwargs):
        super().__init__(**kwargs)

        self.reorderable_list = ft.ReorderableListView(
            show_default_drag_handles=False,
            controls=[],
            expand=1,
            # auto_scroll=True,
            height=page.height,
            on_reorder=lambda e: self.handle_reorder(e, state, self.update_list_controls),
            on_size_change=lambda e: self.handle_size_change(e),
            footer=AddGroupWidget(update_callback=self.update_list_controls),
        )

        self.state = state

        self.update_list_controls()

        self.button_preview = ButtonSizePreview()

        self.max_time_to_choose = AppSettingsWidget(
            setting=AppSettingsEnum.MAX_TIME_TO_CHOOSE,
            value_picker=NumberPicker(minimum=0),
            description="Maximum time to chose a word",
            data=page.data.settings)
        self.time_between = AppSettingsWidget(
            setting=AppSettingsEnum.TIME_TO_WAIT_BETWEEN,
            value_picker=NumberPicker(step=0.5, minimum=0),
            description="Time to wait between 2 word groups",
            data=page.data.settings)
        self.gaze_per_second = AppSettingsWidget(
            setting=AppSettingsEnum.GAZE_PER_SECOND,
            value_picker=NumberPicker(step=1, minimum=0),
            description="Number of gaze the app will try to make every second",
            data=page.data.settings)
        self.button_size = AppSettingsWidget(
            setting=AppSettingsEnum.BUTTONS_SIZE,
            value_picker=SliderPicker(),
            description="Size of the buttons",
            data=page.data.settings,
            to_update=[self.button_preview]
        )

        self.controls = [
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            self.reorderable_list,
                        ],
                        expand=True
                    ),
                    ft.VerticalDivider(),
                    ft.Column(
                        controls=[
                            self.max_time_to_choose,
                            self.time_between,
                            self.gaze_per_second,
                            self.button_size,
                            self.button_preview,
                            ft.Row(
                                controls=[
                                    ft.Button(content="Load CSV", on_click=lambda _: page.run_task(loadCSV, page)),
                                    ft.Button(content="Save To CSV", on_click=lambda _: page.run_task(self.save_experience, state)),
                                    ft.Button(content="Go Back", on_click=lambda _: page.run_task(self.go_back),
                                              ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY
                            )
                        ],
                        expand=True,
                    ),
                ],
                expand=True,
            )
        ]
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.expand = True

    async def save_experience(self, state: AppState):
        if self.check_values():
            await saveExperimentToCSV(state)

    def check_values(self):
        val = True
        for e in self.reorderable_list.controls:
            if isinstance(e, GroupCustomization):
                if not e.check_values():
                    val = False

        if not val:
            snackbar = ft.SnackBar(
                content=ft.Text("Some groups have empty words"),
                duration=2000,
                behavior=ft.SnackBarBehavior.FLOATING
            )
            self.page.show_dialog(snackbar)

        return val

    async def go_back(self):
        if self.check_values():
            await self.page.push_route("/WordExperiment")

    def update_list_controls(self, go_down: bool = False):
        """Update (or initiate) GroupCustomization widgets is the list
        :param go_down: Whether the list should scroll to the last element, default to False
        :type go_down: bool
        """
        self.reorderable_list.controls = []
        for index, group in enumerate(self.state.word_groups):
            self.reorderable_list.controls.append(GroupCustomization(group_index=index, word_group=group, update_callback=self.update_list_controls))
        if go_down:
            async def scroll_delayed():
                await asyncio.sleep(0.05) # Un battement de cil pour laisser le rendu se faire
                await self.reorderable_list.scroll_to(offset=-1)

            self.page.run_task(scroll_delayed)

@ft.control
class AddGroupWidget(ft.Container):
    def __init__(self, update_callback, **kwargs):
        self.update_callback = update_callback
        super().__init__(**kwargs)

        self.content = ft.Row(
            controls=[
                ft.Text(value="Add New Word Group", size=12 * TEXT_SIZE, weight=ft.FontWeight.W_600),
                ft.Icon(
                    icon=ft.Icons.ADD_BOX,
                    color=ft.Colors.BLUE,
                )
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.border = ft.Border.all(1, ft.Colors.BLUE)
        self.bgcolor = ft.Colors.LIGHT_BLUE_ACCENT_100
        self.border_radius = ft.BorderRadius.all(10)
        self.on_click = self.handle_click
        self.ink = True

    def handle_click(self):
        self.page.data.word_groups.append(WordGroup())

        self.update_callback(True)


@ft.control
class RemoveGroupWidget(ft.IconButton):
    def __init__(self, group_index, update_callback, **kwargs):
        self.update_callback = update_callback
        self.group_index = group_index
        super().__init__(**kwargs)
        self.on_click = self.handle_click
        self.icon = ft.Icons.DELETE
        self.icon_color = ft.Colors.RED

    def handle_click(self):
        self.page.data.word_groups.pop(self.group_index)
        self.update_callback()


@ft.control
class CorrectAnswerDropdown(ft.Dropdown):

    def __init__(self, word_group: WordGroup, **kwargs):
        self.word_group = word_group
        super().__init__(**kwargs)

        self.options = []

        for index, word in enumerate(self.word_group.words):
            self.options.append(ft.DropdownOption(key=str(index), text=word))

        self.index: int = word_group.words.index(self.word_group.correct)

        self.value = str(self.index)

        self.on_select = self.handle_select

    def handle_select(self, e):
        self.word_group.correct = self.word_group.words[int(e.control.value)]
        self.index = int(e.control.value)

    def update_list(self):
        self.options = []
        for index, word in enumerate(self.word_group.words):
            self.options.append(ft.DropdownOption(key=str(index), text=word))
        self.word_group.correct = self.word_group.words[self.index]
        self.update()


@ft.control
class SoundPicker(ft.Container):
    """Display the selected sound and allow replaying it."""

    def __init__(self, word_group: WordGroup, **kwargs):
        super().__init__(content=None, **kwargs)

        self.word_group = word_group

        self.choose_sound_button = ft.Button(content=word_group.sound)
        self.play_sound_button = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW,
            icon_color=ft.Colors.BLUE,
            icon_size=40,
        )

        self.content = ft.Row(
            controls=[self.choose_sound_button, self.play_sound_button],
        )
        self.border = ft.Border.all(1, ft.Colors.GREY)
        self.border_radius = ft.BorderRadius.all(15)
        self.animate=ft.Animation(duration=1000, curve=ft.AnimationCurve.BOUNCE_IN_OUT)

        self.padding = ft.Padding.all(5)

    def build(self):
        self.choose_sound_button.on_click = lambda _: self.page.run_task(self.choose_sound)
        self.play_sound_button.on_click = lambda _: self.page.run_task(self.play_sound)

    async def play_sound(self):
        await playSound(self.word_group.sound)

    def update_text(self):
        self.choose_sound_button.content = self.word_group.sound.split("/")[-1]
        self.update()

    async def choose_sound(self):
        file_path = await ft.FilePicker().pick_files(allow_multiple=False)

        if file_path:
            self.word_group.sound = file_path[0].path
        self.update_text()


@ft.control
class GroupCustomization(ft.Container):
    """Widget used to edit one WordGroup."""

    def __init__(self, group_index: int, word_group: WordGroup, update_callback, **kwargs):
        self.group_index: int = group_index
        self.word_group: WordGroup = word_group
        self.update_callback = update_callback

        super().__init__(**kwargs)

        self.expand = True
        self.padding = 10
        self.margin = ft.Margin.symmetric(vertical=2.5)
        self.border = ft.Border.all(3, ft.Colors.BLUE_ACCENT)
        self.border_radius = ft.BorderRadius.all(5)

        self.word_picker = WordPicker(on_word_change=self.update_correct_dropdown, word_group=self.word_group)
        self.sound_picker = SoundPicker(word_group=self.word_group)
        self.correct_answer_dropdown = CorrectAnswerDropdown(word_group=self.word_group)

        self.content = ft.Row(
            controls=[
                self.word_picker,
                ft.Column(
                    controls=[
                        self.sound_picker,
                        ft.Row(
                            controls=[
                                ft.Text("Correct Answer : "),
                                self.correct_answer_dropdown,

                            ]
                        )
                    ]
                ),
                ft.Column(controls=[
                    RemoveGroupWidget(group_index=group_index, update_callback=self.update_callback),
                    ft.ReorderableDragHandle(
                        content=ft.Icon(ft.Icons.DRAG_INDICATOR, color=ft.Colors.BLUE),
                        mouse_cursor=ft.MouseCursor.GRAB,
                    ),
                ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True,
                )
            ],
            expand=1,
        )

    def update_correct_dropdown(self):
        self.correct_answer_dropdown.update_list()

    def remove_word_group(self):
        self.page.data.word_groups.remove(self.word_group)

    def check_values(self):
        res = True

        if self.word_group.sound == "":
            self.sound_picker.border = ft.Border.all(3, ft.Colors.RED)
            res = False


        for word in self.word_group.words:
            if word == "":
                res = False
                self.alert_empty()

        return res

    def alert_empty(self):
        for tile in self.word_picker.tiles:
            if tile.text_field.content.value == "":
                # tile.text_field.border_color = ft.Colors.RED
                # tile.text_field.border_width = 3
                tile.text_field.border = ft.Border.all(3, ft.Colors.RED)

        self.page.update()


@ft.control
class WordPicker(ft.Column):
    """Display a 2x2 editable grid for one WordGroup."""

    def __init__(self, on_word_change, word_group: WordGroup, **kwargs):
        super().__init__(controls=None, **kwargs)

        self.word_group = word_group

        self.expand = True
        self.validate_words()
        self.tiles: list[DragTile] = []
        self.build_grid()
        self.on_word_change = on_word_change

    def validate_words(self):
        if len(self.word_group.words) != WORDS_PER_GROUP:
            raise ValueError(
                f"Each WordGroup must contain exactly {WORDS_PER_GROUP} words. "
                f"Received {len(self.word_group.words)}."
            )

    def build_grid(self):
        self.tiles = [
            DragTile(self.word_group.words[index], index, self.handle_swap, self.handle_change_word)
            for index, word in enumerate(self.word_group.words)
        ]

        self.controls = [
            ft.Row(controls=self.tiles[:2], expand=True),
            ft.Row(controls=self.tiles[2:4], expand=True),
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
        self.on_word_change()


@ft.control
class DragTile(ft.DragTarget):
    def __init__(self, word: str, index: int, on_swap, on_change, **kwargs):
        self.text_field = ft.Container(
            content=ft.TextField(
                value=word,
                on_change=lambda e, tile_index=index: on_change(tile_index, e.control.value),
                expand=True,
                border=ft.InputBorder.NONE,
            ),
            padding=ft.Padding().all(5),
            border=ft.Border.all(1, ft.Colors.BLACK),
            border_radius=ft.BorderRadius.all(5),
            animate=ft.Animation(duration=1000, curve=ft.AnimationCurve.BOUNCE_IN_OUT)
        )

        self.container = ft.Container(expand=True, content=self.text_field, width=100, height=100, alignment=ft.Alignment.CENTER, )
        content = ft.Draggable(
            expand=True,
            content=self.container,
            data=index,
        )

        super().__init__(content=content, **kwargs)
        self.content = content
        self.on_accept = on_swap
        self.data = index
        self.expand = True


@ft.control
class ValuePicker(ft.Row):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.built = False

        self.value = 0.0

        self.text_field = ft.TextField()

    def build(self):
        self.built = True

    def set_value_updater(self, method: Callable):
        self.text_field.on_change = method

    def set_value(self, value):
        self.value = value
        self.update_shown()

    def update_shown(self):
        """Updates the value shown based on widget value"""
        self.text_field.value = str(self.value)
        if self.built:
            self.update()


@ft.control
class AppSettingsWidget(ft.Container):
    """The widget used to modify any parameter in AppSettings. Store the reference of the AppSettings in his Data attribute."""

    def __init__(self, setting: AppSettingsEnum, value_picker: ValuePicker, description: str, to_update=None, **kwargs):
        if to_update is None:
            to_update = []
        self.setting = setting
        self.value_picker = value_picker
        self.description = description
        self.to_update = to_update

        super().__init__(**kwargs)

        value = getattr(self.data, self.setting.value)
        self.value_picker.value = value
        self.value_picker.set_value(value)
        self.value_picker.set_value_updater(self.update_intern_value)

        self.content = ft.Row(
            controls=[
                ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.BLUE, expand=1),
                self.value_picker,
                ft.Text(value=self.description, weight=ft.FontWeight.W_600, expand=8),
            ],
            tight=True
        )

    def update_intern_value(self, e, new_value=None):
        """Updates the value in the App setting and in the Picker Object"""
        if new_value is None:
            if new_value == "":
                new_value = 0.0
            else:
                new_value = float(e.control.value)
        self.value_picker.set_value(new_value)
        setattr(self.page.data.settings, self.setting.value, new_value)
        self.value_picker.update_shown()
        self.update()

        for ctrl in self.to_update:
            ctrl.update()


@ft.control
class NumberPicker(ValuePicker):

    def __init__(self, step: float = 1.0, minimum: float = None, **kwargs):
        super().__init__(**kwargs)

        self.step = step
        self.minimum = minimum
        self.value = "0"

        self.text_field = ft.TextField(value=self.value,
                                       keyboard_type=ft.KeyboardType.NUMBER,
                                       input_filter=ft.InputFilter(allow=True, regex_string=r"^(\d+\.)?\d*$", replacement_string=""),
                                       expand_loose=True,
                                       text_align=ft.TextAlign.CENTER,
                                       )

        self.controls = [
            ft.IconButton(icon=ft.Icons.REMOVE, on_click=self.button_down),
            self.text_field,
            ft.IconButton(icon=ft.Icons.ADD, on_click=self.button_up),
        ]

        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

    def button_up(self, e):
        new_val = float(self.value) + self.step
        if self.minimum is not None:
            if new_val < self.minimum:
                return
        self.text_field.on_change(e, new_val)

    def button_down(self, e):
        new_val = float(self.value) - self.step
        if self.minimum is not None:
            if new_val < self.minimum:
                return
        self.text_field.on_change(e, new_val)


@ft.control
class SliderPicker(ValuePicker):

    def set_value_updater(self, method: Callable):
        super().set_value_updater(method)
        self.slider.on_change = method

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = 0.0

        self.built = False
        self.slider = ft.Slider(value=self.value)
        self.text_field = ft.TextField(value=str(self.value),
                                       keyboard_type=ft.KeyboardType.NUMBER,
                                       input_filter=ft.InputFilter(allow=True, regex_string=r"^(\d+\.)?\d*$", replacement_string=""),
                                       expand_loose=True,
                                       width=100,
                                       text_align=ft.TextAlign.CENTER,
                                       )

        self.controls = [
            self.slider,
            self.text_field
        ]

    def set_value(self, value):
        if value > 1:
            value = 1.0
        self.value = value
        self.update_shown()

    def update_shown(self):
        """Updates the value shown based on widget value"""
        self.slider.value = self.value
        super().update_shown()
        if self.built:
            parent = self.parent
            if parent:
                parent.update()


@ft.control
class ButtonSizePreview(ft.Container):

    def __init__(self, size: float = 0.5, **kwargs):
        super().__init__(**kwargs)
        self.size = size

        self.aspect_ratio = 16 / 9
        self.buttons = [
            ft.Container(
                content=ft.Button(content=ft.Text(content, size=76 * self.size)),
                expand=1,
                alignment=ft.Alignment.CENTER,
            )
            for content in ["A", "B", "C", "D"]
        ]

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=self.buttons[:2],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                ),
                ft.Row(
                    controls=self.buttons[2:4],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )

        self.expand = True
        self.on_size_change = self.handle_resize
        self.border = ft.Border.all(2, ft.Colors.GREY)

    def before_update(self) -> None:
        self.resize_buttons()

    def resize_buttons(self):
        self.size = self.page.data.settings.buttons_size

        for button in self.buttons:
            button.content.width = max((self.width or 1920) / 2, 200) * self.size * 0.95
            button.content.height = max((self.height or 1080) / 2, 140) * self.size * 0.95

            button.content.content.size = 76 * self.size

    def handle_resize(self, e):
        self.width = e.width
        self.height = e.height
