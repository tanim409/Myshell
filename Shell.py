import sys,signal

from readline import set_completer_delims

from Prompt import Prompt
from Executor import Executor
from Parser import Parser
from Builtin import Builtin
from Config import IS_WINDOWS, Has_Readline, readline
from Color import Color
from History import History
from Completer import Completer


class Shell:
    version = "1.0.0"

    def __init__(self):
        self.exit_code: int = 0
        self.running: bool = True
        self.last_exit: int = 0
        self.prev_dir = ''
        self.prompt = Prompt()
        self.aliases: dict = {}
        self.executor = Executor(self)
        self.parser = Parser()
        self.Builtin = Builtin(self)
        self.history = History()
        self.color = Color()
        self.completer = Completer()

    def setup_readline(self):
        if not Has_Readline or readline is None:
            return
        if Has_Readline:
            readline.set_completer(self.completer.complete)
            readline.set_completer_delims(' \t\n;')
            try:
                readline.parse_and_bind("tab: complete")
            except Exception:
                try:
                    readline.parse_and_bind("tab: menu-complete")
                except Exception:
                    pass

    def setup_signal(self):
        signal.signal(signal.SIGINT, self.handle_sigInt)
        if hasattr(signal, 'SIGQUIT'):
            signal.signal(signal.SIGQUIT, signal.SIG_IGN)

    def handle_sigInt(self, sig, frame):
        print()

    def print_banner(self):
        print(self.color.c(Color.CYAN, r"""
 __  __       ____  _          _ _
|  \/  |_   _/ ___|| |__   ___| | |
| |\/| | | | \___ \| '_ \ / _ \ | |
| |  | | |_| |___) | | | |  __/ | |
|_|  |_|\__, |____/|_| |_|\___|_|_|
        |___/     
        
      """))

        platform = "Windows" if IS_WINDOWS else sys.platform.capitalize()
        print(self.color.c(Color.BLUE, f"v{self.version} | python : {sys.version.split()[0]} | {platform}"))
        print(self.color.c(Color.GREEN, "Type 'help' command for help. exit for quit.\n"))

    def run(self):
        self.print_banner()
        self.setup_readline()
        self.setup_signal()
        while self.running:
            line = input(self.prompt.build(self.last_exit))
            if not line.strip():
                continue
            self.history.add(line)
            self.execute_line(line)

    def execute_line(self, line):
        command = line.strip()
        if not command:
            return
        cmd = self.parser.parse(command)
        self.executor.execute(cmd)


shell = Shell()
shell.run()
