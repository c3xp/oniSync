import tkinter as tk
from tkinter import ttk

from controller import BPMToolController


def main() -> None:
    root = tk.Tk()

    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass

    BPMToolController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
