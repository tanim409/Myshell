import sys

IS_WINDOWS = sys.platform.startswith('win')

try:
    import readline
    Has_Readline = True
except ImportError:
    try:
        import pyreadline3 as readline
        Has_Readline = True
    except ImportError:
        readline = None
        Has_Readline = False