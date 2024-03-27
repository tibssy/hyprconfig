from typing import List, Optional

from flet import RoundedRectangleBorder, BoxShadow, UserControl, LinearGradient
from flet_core.buttons import ButtonStyle
from flet_core.control import OptionalNumber
from flet_core.types import MainAxisAlignment, Padding, Margin, Offset, BorderRadiusValue, ScaleValue
from flet_core import (
    AlertDialog,
    Stack,
    Container,
    Column,
    Row,
    Slider,
    ElevatedButton,
    alignment
)
import colorsys


class GradientSlider(UserControl):
    def __init__(
            self,
            colors: List = None,
            value: OptionalNumber = None,
            shadow=None,
            on_change=None
    ):
        super().__init__()
        self.shadow = shadow
        self.colors = colors
        self.value = value
        self.on_change = on_change
        self.container = Container(
            margin=Margin(9, 1, 9, 0),
            height=28,
            border_radius=14,
            offset=Offset(0, 0.3),
            alignment=alignment.center,
            shadow=self.shadow
        )
        self.slider = Slider(
            active_color='#00000000',
            inactive_color='#00000000',
            thumb_color='#aaffffff',
            min=0,
            max=1024,
            value=self.value,
            on_change=self.on_value
        )

    def build(self):
        self.container.gradient = LinearGradient(
            begin=alignment.center_left,
            end=alignment.center_right,
            colors=self.colors
        )
        return Stack(
            controls=[
                self.container,
                self.slider
            ]
        )

    def on_value(self, e):
        if self.on_change:
            self.on_change(e)


class RoundedElevatedButton(ElevatedButton):
    def __init__(
            self,
            text: Optional[str] = None,
            bgcolor: Optional[str] = None,
            color: Optional[str] = None,
            radius: BorderRadiusValue = None,
            scale: ScaleValue = None,
            on_click=None
    ):
        super().__init__()
        self.text = text
        self.bgcolor = bgcolor
        self.color = color
        self.style = ButtonStyle(shape=RoundedRectangleBorder(radius=radius))
        self.elevation = 2
        self.scale = scale
        self.on_click = on_click

    def click(self):
        if callable(self.on_click):
            self.on_click()


class ColorSelector(AlertDialog):
    def __init__(self, on_color=None):
        super().__init__()
        self.on_color = on_color
        self.shadow = None
        self.hue_slider = None
        self.saturation_slider = None
        self.value_slider = None
        self.color_indicator = None
        self.control_row = None
        self.open_button = None
        self.slider_range = None
        self.initialize_components()
        self.setup_ui()

    def initialize_components(self):
        slider_colors = {
            'hue': ['#ff0000', '#ffff00', '#00ff00', '#00ffff', '#0000ff', '#ff00ff', '#ff0000'],
            'saturation': ['#ffffff', '#ff0000'],
            'value': ['#000000', '#ff0000']
        }
        self.slider_range = 1024
        self.shadow = BoxShadow(
            spread_radius=0,
            blur_radius=2,
            color='#9f9f9f',
            offset=(0, 2)
        )
        self.color_indicator = Container(
            alignment=alignment.center,
            expand=True,
            height=30,
            bgcolor='#ff0000',
            border_radius=6,
            shadow=self.shadow
        )
        self.hue_slider = self.create_gradient_slider(*slider_colors.get('hue'), initial_value=0)
        self.saturation_slider = self.create_gradient_slider(*slider_colors.get('saturation'), initial_value=1024)
        self.value_slider = self.create_gradient_slider(*slider_colors.get('value'), initial_value=1024)
        self.control_row = self.create_control_row()

    def setup_ui(self):
        self.modal = True
        self.shape = RoundedRectangleBorder(radius=10)
        self.content_padding = Padding(10, 10, 10, 0)
        self.elevation = 10
        self.content = Column(
            width=400,
            height=200,
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.control_row,
                self.hue_slider,
                self.saturation_slider,
                self.value_slider
            ]
        )

    def create_gradient_slider(self, *colors, initial_value):
        return GradientSlider(
            shadow=self.shadow,
            value=initial_value,
            on_change=self.on_slider_change,
            colors=list(colors)
        )

    def create_control_row(self):
        return Row(
            spacing=12,
            controls=[
                RoundedElevatedButton(
                    text='Cancel',
                    radius=6,
                    on_click=self.close_dialog
                ),
                self.color_indicator,
                RoundedElevatedButton(
                    text='Select',
                    radius=6,
                    on_click=self.save_color
                )
            ]
        )

    def on_slider_change(self, e):
        color_value = self.get_hue_color()
        self.saturation_slider.colors[-1] = color_value
        self.value_slider.colors[-1] = color_value
        self.saturation_slider.update()
        self.value_slider.update()
        self.update_color_indicator()

    def update_color_indicator(self):
        hsv_color = (
            self.hue_slider.slider.value / self.slider_range,
            self.saturation_slider.slider.value / self.slider_range,
            self.value_slider.slider.value / self.slider_range
        )
        self.color_indicator.bgcolor = self.hsv_to_hex(hsv_color)
        self.color_indicator.update()

    def save_color(self, e):
        if self.open_button.bgcolor != self.color_indicator.bgcolor:
            self.open_button.bgcolor = self.color_indicator.bgcolor
            if callable(self.on_color):
                self.on_color(self.color_indicator.bgcolor)
        self.close_dialog(e)

    def get_hue_color(self) -> str:
        rgb_color = colorsys.hsv_to_rgb(self.hue_slider.slider.value / self.slider_range, 1, 1)
        return self.rgb_to_hex(rgb_color)

    def hex_to_rgb(self, hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def hex_to_hsv(self, hex_color: str) -> tuple:
        return colorsys.rgb_to_hsv(*self.hex_to_rgb(hex_color))

    def rgb_to_hex(self, rgb_color: tuple) -> str:
        r, g, b = rgb_color
        return f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'

    def hsv_to_hex(self, hsv_color: tuple) -> str:
        return self.rgb_to_hex(colorsys.hsv_to_rgb(*hsv_color))

    def update_sliders(self):
        if self.open_button.bgcolor:
            self.color_indicator.bgcolor = self.open_button.bgcolor
            h, s, v = self.hex_to_hsv(self.open_button.bgcolor)
            self.hue_slider.slider.value = h * self.slider_range
            self.saturation_slider.slider.value = s * self.slider_range
            self.value_slider.slider.value = v / 255 * self.slider_range
            hue_color = self.get_hue_color()
            self.saturation_slider.colors[-1] = hue_color
            self.value_slider.colors[-1] = hue_color
            if self.page:
                self.hue_slider.update()
                self.saturation_slider.update()
                self.value_slider.update()

    def open_dialog(self, e):
        if not e.page.dialog:
            e.page.dialog = self
        self.open_button = e.control
        self.update_sliders()
        self.open = True
        e.page.update()

    def close_dialog(self, e):
        self.open = False
        self.open_button.update()
        e.page.update()
        e.page.dialog = None
