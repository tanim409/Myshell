import os
from pyclbr import readmodule_ex
from Config import IS_WINDOWS
from Color import Color


class Builtin:
    def __init__(self, Shell):
        self.Shell = Shell
        self.Color = Color()
        self.commands: dict = {
            'cd': self.cmd_cd,
            'pwd': self.cmd_pwd,
            'echo': self.cmd_echo,
            'export': self.cmd_export,
            'unset': self.cmd_unset,
            'env': self.cmd_env,
            'clear': self.cmd_clear,
            'alias': self.cmd_aliases,
            'help': self.cmd_help,
            'history': self.cmd_history,
            'exit': self.cm_exit
        }

    def is_builtin(self, command: str) -> bool:
        return command in self.commands

    def run(self, args: list):
        return self.commands[args[0]](args[1:])

    def cmd_history(self, args):
        n = int(args[0]) if args else 20
        self.Shell.history.show(n)
        return 0

    def cmd_cd(self, args):
        if not args or args[0] == '~':
            target = os.path.expanduser('~')
        elif args[0] == '-':
            target = self.Shell.prev_dir or os.path.expanduser('~')
        else:
            target = os.path.expandvars(os.path.expanduser(args[0]))
        try:
            self.Shell.prev_dir = os.getcwd()
            os.chdir(target)
            return 0
        except FileNotFoundError:
            print(self.Color.c(Color.RED, '[!] File not found!'))
            return 1
        except PermissionError:
            print(self.Color.c(Color.RED, '[!] Permission denied!'))
            return 1

    def cmd_pwd(self, args):
        print(os.getcwd())
        return 0

    def cmd_echo(self, args):
        newline = True
        if args and args[0] == '-n':
            newline = False
            args = args[1:]
        text = os.path.expandvars(' '.join(args))
        print(text, end='\n' if newline else '')
        return 0

    def cmd_export(self, args):
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                key = key.strip()
                value = value.strip()
                os.environ[key] = value
            else:
                print('Invalid Format')
        return 0

    def cmd_unset(self, args):
        for arg in args:
            os.environ.pop(arg, None)
        return 0

    def cmd_env(self, args):
        for key, val in sorted(os.environ.items()):
            print(key, '=', val)
        return 0

    def cmd_clear(self, args):
        if IS_WINDOWS:
            os.system('cls')
        else:
            print(end='')
        return 0

    def cmd_aliases(self, args):
        if not args:
            return 0

        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                key = key.strip()
                value = value.strip()
                self.Shell.aliases[key] = value.strip("'/")
                print(f"alias {key}={value} created")
                return 0
            else:
                print(self.Color.c(Color.RED, 'use proper format!'))

        return 0

    def cmd_help(self, args):
        print()
        print("Builtin Commands:")
        print(' -' * 28)
        cmds = [
            ("cd [dir]", "Change dir. cd ~ = home, cd - = previous"),
            ("pwd", "Print current working directory"),
            ("echo [-n] [text]", "Print text. Expands $VARS"),
            ("export KEY=VALUE", "Set environment variable"),
            ("unset KEY", "Remove environment variable"),
            ("env", "List all environment variables"),
            ("alias name='cmd'", "Create a command alias"),
            ("history [n]", "Show last n commands (default 20)"),
            ("clear", "Clear the terminal screen"),
            ("exit [code]", "Exit with optional code"),
            ("help", "Show this help message"),
        ]
        for cmd, desc in cmds:
            print(f"{cmd : <26}{desc}")

        print()
        for cmd, desc in [('|', 'Pipe'), ('>', 'Overwrite file'), ('>>', 'Append file'), ('<', 'Read from file')]:
            print(f"{cmd : <26}{desc}")

    def cm_exit(self, args):
        self.Shell.running = False
        return 0
