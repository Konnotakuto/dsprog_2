import flet as ft
import math


class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text


class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24
        self.color = ft.Colors.WHITE


class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE
        self.color = ft.Colors.WHITE


class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_100
        self.color = ft.Colors.BLACK


class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment=ft.MainAxisAlignment.END),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="x²", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="sin", button_clicked=self.button_clicked),
                        ExtraActionButton(text="cos", button_clicked=self.button_clicked),
                        ExtraActionButton(text="tan", button_clicked=self.button_clicked),
                        ActionButton(text="x/y", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="x!", button_clicked=self.button_clicked),
                        ExtraActionButton(text="√", button_clicked=self.button_clicked),
                        ExtraActionButton(text="-x", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                )
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data, type(data)}")

        try:
            if self.result.value == "Error" or data == "AC":
                self.result.value = "0"
                self.reset()

            elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
                if self.result.value == "0" or self.new_operand == True:
                    self.result.value = data
                    self.new_operand = False
                else:
                    self.result.value = self.result.value + data

            elif data in ("+", "-", "*", "/"):
                result_val = float(self.result.value)
                self.result.value = str(self.calculate(self.operand1, result_val, self.operator))
                self.operator = data
                if self.result.value == "Error":
                    self.operand1 = 0
                else:
                    self.operand1 = float(self.result.value)
                self.new_operand = True

            elif data == "=":
                result_val = float(self.result.value)
                self.result.value = str(self.calculate(self.operand1, result_val, self.operator))
                self.reset()

            elif data == "%":
                result_val = float(self.result.value)
                self.result.value = str(result_val / 100)
                self.reset()

            elif data == "+/-":
                result_val = float(self.result.value)
                if result_val > 0:
                    self.result.value = "-" + self.result.value
                elif result_val < 0:
                    self.result.value = str(self.format_number(abs(result_val)))

            elif data in ("sin", "cos", "tan"):
                result_val = float(self.result.value)
                angle_in_radians = math.radians(result_val)
                if data == "sin":
                    self.result.value = str(self.format_number(math.sin(angle_in_radians)))
                elif data == "cos":
                    self.result.value = str(self.format_number(math.cos(angle_in_radians)))
                elif data == "tan":
                    self.result.value = str(self.format_number(math.tan(angle_in_radians)))
                self.new_operand = True

            elif data == "√":
                result_val = float(self.result.value)
                if result_val < 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(self.format_number(math.sqrt(result_val)))
                self.new_operand = True

            elif data == "-x":
                result_val = float(self.result.value)
                self.result.value = str(self.format_number(-1 * result_val))
                self.new_operand = True

            elif data == "x/y":
                result_val = float(self.result.value)
                self.result.value = str(self.calculate(self.operand1, result_val, self.operator))
                self.operator = "/"
                if self.result.value == "Error":
                    self.operand1 = 0
                else:
                    self.operand1 = float(self.result.value)
                self.new_operand = True

            elif data == "x²":
                result_val = float(self.result.value)
                self.result.value = str(self.format_number(result_val ** 2))
                self.new_operand = True

            elif data == "x!":
                result_val = float(self.result.value)
                if result_val < 0 or result_val != int(result_val):
                    self.result.value = "Error"
                else:
                    self.result.value = str(self.format_number(math.factorial(int(result_val))))
                self.new_operand = True

        except (ValueError, OverflowError):
            self.result.value = "Error"
            self.reset()

        self.update()

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            return num

    def calculate(self, operand1, operand2, operator):
        if operator == "+":
            return self.format_number(operand1 + operand2)
        elif operator == "-":
            return self.format_number(operand1 - operand2)
        elif operator == "*":
            return self.format_number(operand1 * operand2)
        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Simple Calculator"
    calc = CalculatorApp()
    page.add(calc)


ft.app(main)
