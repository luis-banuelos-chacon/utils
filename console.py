import termios
import select
import sys
import tty


def getKey():
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.read(1)

term_settings = termios.tcgetattr(sys.stdin)
try:
    tty.setcbreak(sys.stdin.fileno())

    while True:

        try:
            key = getKey()
            if key:
                print(repr(key))

        except KeyboardInterrupt:
            break

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, term_settings)
