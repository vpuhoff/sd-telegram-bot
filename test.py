import random

from gyverhubd import Device, run_server, Color, Layout
from gyverhubd.proto.websocket import WebsocketProtocol


class MyDevice(Device):
    name = "Test"

    @Layout
    def ui(self, ui: Layout):
        tabs = ui.Tabs(items=("TAB 4", ))

        with tabs.tab("1"):
            ui.Button("Button 1")
            ui.Button("Button 2", color=Color.RED)
            ui.ButtonIcon("")
            ui.ButtonIcon("", color=Color.AQUA)

            with ui.rows(cols=3, height=100):
                ui.Label("Status")
                ui.Led("Status")
                ui.Led("Icon", text="")

            ui.Title("Inputs")

            with ui.rows():
                ui.Input("String input", regex="^[A-Za-z]+$")
                ui.Input("cstring input")
                ui.Input("int input")
                ui.Input("float input")

            ui.Password("Pass input", color=Color.RED)

            ui.Slider("Slider")
            ui.Slider("Slider F", min=0, value=10, max=90, step=0.5, color=Color.PINK)

            with ui.rows(width=60):
                ui.Gauge("Temp", text="°C", value=random.randrange(-5, 30), min=-5, max=30, step=0.1, color=Color.RED)

        with tabs.tab("2"):
            ui.Joystick(auto=True)

            ui.Spinner("Spinner")
            ui.Spinner("Spinner F", value=0, min=0, max=10, step=0.5)

            ui.Switch("My switch")
            ui.SwitchIcon("My switch i", text="", color=Color.BLUE)
            ui.SwitchText("My switch t", text="ON", color=Color.VIOLET)
            ui.ColorSelect("Color")

            ui.Date("Date select", color=Color.RED)
            ui.Time("Time select", color=Color.YELLOW)

            ui.DateTime("Date time")

        with tabs.tab("3"):
            ui.Select("List picker", items=("kek", "puk", "lol"))
            ui.Flags("My flags", items=("mode 1", "flag", "test"), color=Color.AQUA)

            ui.Display("", color=Color.BLUE)
            ui.Html("some custom\n<strong>Text</strong>")

            ui.Log("text")

        with tabs.tab("Canvas"):
            cv = ui.Canvas("label", width=90, height=80, active=True)

        @cv.clicked
        def _(_, coords):
            x, y = coords
            cmd_list = ['fillStyle', 'strokeStyle', 'shadowColor', 'shadowBlur', 'shadowOffsetX', 'shadowOffsetY',
                        'lineWidth', 'miterLimit', 'font', 'textAlign', 'textBaseline', 'lineCap', 'lineJoin',
                        'globalCompositeOperation', 'globalAlpha', 'scale', 'rotate', 'rect', 'fillRect',
                        'strokeRect', 'clearRect', 'moveTo', 'lineTo', 'quadraticCurveTo', 'bezierCurveTo',
                        'translate', 'arcTo', 'arc', 'fillText', 'strokeText', 'drawImage', 'roundRect', 'fill',
                        'stroke', 'beginPath', 'closePath', 'clip', 'save', 'restore']

            cv.commands = (f"{cmd_list.index('fillStyle')}:{(Color.RED << 8) | 0xFF}",
                           f"{cmd_list.index('fillRect')}:{x},{y},5,5")


if __name__ == '__main__':
    run_server(MyDevice(), protocols=[WebsocketProtocol()])