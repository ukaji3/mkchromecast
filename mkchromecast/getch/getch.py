try:
    from msvcrt import getch  # type: ignore[attr-defined]  # Windows only
except ImportError:

    def getch():
        """
        Gets a single character from STDIO.
        """
        import sys
        import tty
        import termios

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
