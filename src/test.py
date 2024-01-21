import weakref


class Temp:
    def __init__(self, arg):
        self.arg = arg


class Button:
    def __init__(self, t):
        self.t = t()

    def push(self):
        print(self.t.arg)


def create_temp_button() -> Button:
    temp = Temp('aa')
    temp_proxy = weakref.ref(temp)
    button = Button(temp_proxy)
    del temp
    return button


b = create_temp_button()
b.push()
