import tkinter as tk
from ui import PlayerSearchApp


def main():
    root = tk.Tk()
    app = PlayerSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()