import tkinter as tk

from ui import WeatherAppUI


def main() -> None:
    """Start the Weather App."""

    root = tk.Tk()

    WeatherAppUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()