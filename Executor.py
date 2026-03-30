import sys

import shlex, glob, os, subprocess
from Config import IS_WINDOWS
from Color import Color


class Executor:
    def __init__(self, shell: 'Shell'):
        self.shell = shell
        self.color = Color()

    def execute(self, cmd):
        if len(cmd) == 1:
            return self.run_single(cmd[0])
        return self.run_pipeline(cmd)

    def run_single(self, cmd):
        token = self.expand_aliases(cmd['tokens'])
        token = self.expand_globs(token)
        redirect_in = cmd['redirect_in']
        redirect_out = cmd['redirect_out']
        append = cmd['append']

        if self.shell.Builtin.is_builtin(token[0]):
            if redirect_out:
                mode = 'a' if append else 'w'
                with open(redirect_out, mode) as f:
                    old_out = sys.stdout
                    sys.stdout = f
                    code = self.shell.Builtin.run(token)
                    sys.stdout = old_out
                    return code
            return self.shell.Builtin.run(token)

        std_src = None
        std_dst = None
        try:
            std_src = open(redirect_in, 'r') if redirect_in else None
            std_dst = open(redirect_out, 'a' if append else 'w') if redirect_out else None

            p = subprocess.run(
                token,
                stdin=std_src,
                stdout=std_dst,
                env=os.environ.copy()
            )
            return p.returncode
        except FileNotFoundError:
            print(self.color.c(Color.RED, f"command not found!{token[0]}\n"))
            return 127
        except PermissionError:
            print(self.color.c(Color.RED, f"permission denied!{token[0]}\n"))
            return 1
        except Exception as e:
            print(self.color.c(Color.RED, f" error : {e}\n"))
            return 1
        finally:
            if std_src:
                std_src.close()
            if std_dst:
                std_dst.close()

    def run_pipeline(self, command):
        process = []
        prev_stdout = None

        for i, cmd in enumerate(command):
            token = self.expand_aliases(cmd['tokens'])
            token = self.expand_globs(token)
            is_last = i == len(command) - 1

            std_src = None
            if cmd['redirect_in']:
                std_src = open(cmd['redirect_in'], 'r')
            elif prev_stdout is not None:
                std_src = prev_stdout

            std_dst = None
            if is_last:
                if cmd['redirect_out']:
                    mode = 'a' if cmd['append'] else 'w'
                    std_dst = open(cmd['redirect_out'], mode)
                else:
                    std_dst = subprocess.PIPE
            try:
                p = subprocess.Popen(
                    token,
                    stdin=std_src,
                    stdout=std_dst,
                    env=os.environ.copy()
                )
                process.append((p, std_src, std_dst))
                prev_stdout = p.stdout
            except FileNotFoundError:
                print(self.color.c(Color.RED, f"file not found!{token[0]}\n"))
                return 127
            except PermissionError:
                print(self.color.c(Color.RED, f"permission denied!{token[0]}\n"))
                return 1
            except Exception as e:
                print(self.color.c(Color.RED, f" error : {e}\n"))
                return 1

        exit_code = 0
        for p, std_src, std_dst in process:
              try:
                 p.wait(timeout=5)
              except subprocess.TimeoutExpired:
                  p.kill()
                  print(self.color.c(Color.RED, "process timeout!"))

              exit_code = p.returncode
              for f in (std_src, std_dst):
                    if f and f is not subprocess.PIPE:
                        f.close()
                    else:
                        pass

        return exit_code

    def expand_aliases(self, tokens):
        if tokens and tokens[0] in self.shell.aliases:
            return shlex.split(self.shell.aliases[tokens[0]]) + tokens[1:]
        return tokens

    def expand_globs(self, tokens):
        expand = []
        for token in tokens:
            if any(c in token for c in ('*', '?', '[')): 
                matches = glob.glob(os.path.expanduser(token))
                expand.extend(sorted(matches) if matches else [token]) 
            else:
                expand.append(token)
        return expand
