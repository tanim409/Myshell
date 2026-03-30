import glob
import os.path
from Config import IS_WINDOWS


class Completer:
    def __init__(self):
        self.matches: list = []

    def complete(self, text: str, state: int):
        if state == 0:
            self.matches = self._get_matches(text)
        try:
            return self.matches[state]
        except IndexError:
            return None

    def _get_matches(self, text: str) -> list:
        if '/' in text or text.startswith('.'):
            matches = glob.glob(text + '*')
            new_matches = []
            for m in matches:
                if os.path.isdir(m):
                    new_matches.append(m + '/')
                else:
                    new_matches.append(m)
            matches = new_matches
        else:
            matches = []
            sep = ';' if IS_WINDOWS else ':'
            for path_dir in os.environ.get('PATH', '').split(sep):
                try:
                    for f in os.listdir(path_dir):
                        if f.startswith(text):
                            matches.append(f)
                except (OSError, PermissionError):
                    continue
            try:
                new_matches = []
                for f in os.listdir('.'):  
                    if f.startswith(text): 
                        if os.path.isdir(f): 
                            new_matches.append(f + '/') 
                        else:
                            new_matches.append(f) 

                matches += new_matches

            except OSError:
                pass
        return sorted(set(matches))



