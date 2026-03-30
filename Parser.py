import os, sys

import shlex


class Parser:
    def parse(self, cmd):
        pipe_segment = self.split_pipes(cmd)
        commands = []
        for c in pipe_segment:
            cmd, redirect_in, redirect_out, append = self.pipe_redirects(c)
            tokens = shlex.split(cmd, posix=False) if cmd.strip() else []
            tokens = [t.strip("'\"") for t in tokens]
            if tokens:
                commands.append({
                    'tokens': tokens,
                    'redirect_in': redirect_in,
                    'redirect_out': redirect_out,
                    'append': append
                })
        return commands

    def split_pipes(self, cmd: str):
        segments = []
        commands = []
        in_quote = False
        quote_char = None
        for c in cmd:
            if c in ("'", '"') and not in_quote:
                in_quote = True
                quote_char = c
                commands.append(c)
            elif c == quote_char and in_quote:
                in_quote = False
                quote_char = None
                commands.append(c)
            elif c == '|' and not in_quote:
                segments.append(''.join(commands))
                commands = []
            else:
                commands.append(c)

        segments.append(''.join(commands))
        return segments

    def pipe_redirects(self, cmd):
        redirect_in = None
        redirect_out = None
        append = False

        tokens = shlex.split(cmd, posix=False) if cmd.strip() else []
        clean = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == '>':
                redirect_out = tokens[i + 1]
                i += 2
            elif token == '>>':
                append = True
                redirect_out = tokens[i + 1]
                i += 2
            elif token == '<':
                redirect_in = tokens[i + 1]
                i += 2
            elif token.startswith('>'):
                redirect_out = token[1:]
                i += 1
            elif token.startswith('>>'):
                append = True
                redirect_out = token[2:]
                i += 1
            elif token.startswith('<'):
                redirect_in = token[1:]
                i += 1
            else:
                clean.append(token)
                i += 1

        rebuilt = ' '.join(shlex.quote(tok) for tok in clean)
        return rebuilt, redirect_in, redirect_out, append
