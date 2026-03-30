import os
from Color import Color
from Config import IS_WINDOWS



class Prompt:
    def __init__(self):
        self._hostname = None
        self.cwd = None
        self.color = Color()

    def build(self,last_exit):
        user = os.environ.get('username' if IS_WINDOWS else 'USER', 'user')
        _hostname = self.hostname()
        cwd = self.short_path()
        status =  self.color.c(Color.YELLOW, '❯') if last_exit == 0 else self.color.c(Color.RED, '❯')
        prompt = [
            self.color.c(Color.YELLOW, user) +
            self.color.c(Color.BLUE, '@') +
            self.color.c(Color.BLUE, _hostname),
            self.color.c(Color.YELLOW, cwd)
        ]
        return f"{' '.join(prompt)}\n{status}"

    def hostname(self):
        try:
            return os.uname().nodename
        except AttributeError:
            import socket
            return socket.gethostname()

    def short_path(self):
        cwd = os.getcwd()
        home = os.path.expanduser("~")
        if cwd.startswith(home):
            cwd = '~' + cwd[len(home):]
        list = cwd.replace('\\', '/').split('/')
        if len(list) > 4:
            cwd = '/'.join(['...'] + list[-3:])
        return cwd.replace("\\", "/")
