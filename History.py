import os
from Color import Color


class History:
    cmd_history = os.path.expanduser('~/.history')

    def __init__(self):
        self.history_file: list = []
        self.color = Color()

    def add(self, command):
        self.history_file.append(command)

    def show(self, n: int):
        history = self.history_file[-n:]
        if not history:
            print(self.color.c(self.color.BOLD,"No history file found."))
        for i,command in enumerate(history,1):
            print(self.color.c(self.color.BOLD,f"{i: < 26} "+command))

