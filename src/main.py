import os
import sys

from app import App

if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')

if __name__ == '__main__':
    app = App()
    app.run()
