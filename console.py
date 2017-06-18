from drawing import *
import termios
import select
import time
import sys
import tty


def getKey():
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.read(1)

if __name__ == '__main__':
    term_settings = termios.tcgetattr(sys.stdin)

    p = Painter(80, 20)
    main = Layout()
    main.tl = 'Test Console'
    hist = Formatter(ha='<', va='_')
    hist.data = []
    cmd = Formatter('')
    main.addItem(hist)
    main.addItem(cmd, 1.1)
    main.render(p)
    p.print()

    try:
        tty.setcbreak(sys.stdin.fileno())

        while True:

            try:
                key = getKey()
                if key is not None:
                    # enter
                    if key == '\n':
                        cmd.data = cmd.data[:-1]
                        hist.data.append(cmd.data)
                        cmd.data = '|'

                    # backspace
                    elif key == '\x7f':
                        cmd.data = cmd.data[:-2]
                        cmd.data += '|'

                    # normal
                    else:
                        cmd.data = cmd.data[:-1]
                        cmd.data += key
                        cmd.data += '|'

                    main.render(p)
                    p.print(True)

            except KeyboardInterrupt:
                break

            time.sleep(0.001)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, term_settings)
