from typing import Any

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import tkinter as tk
import numpy as np
import threading
import time


class RealtimePlotter(object):
    """
    Class that manages a popup Tkinter window which can plot data generated on an external thread on-demand.
    Blocks the main thread upon execution.

    Public Methods:
        update_plot(x_data, y_data) -> Provides updated data to plot.
        close_window() -> Closes the TKinter window and liberates the main thread.
    """

    def __init__(
            self,
            title: str,
            x_axis_title: str,
            y_axis_title: str,
            refresh_rate: float = 5
    ):
        """
        Instantiates the RealtimePlotter object by creating the root instance of tkinter under self.root.
        Does not open the popup window yet!

        Args -> TBD (maybe some stuff to process incoming data or make the plot more beautiful):
            title: Title of the window to be displayed

        """
        self.root = tk.Tk()

        # Some Eye-Candy Settings for the General TK Frame
        # TODO: Make these things look beautiful
        self.root.title("EToad – I'm Measuring for You!")
        self.root.geometry(f"{int(self.root.winfo_screenwidth() / 2)}x{int(self.root.winfo_screenheight() / 2)}")
        label = tk.Label(self.root, text=title)
        label.pack(pady=10, padx=10)
        self.refresh_time: int = int(1000 / refresh_rate)

        # Sets up the Plot Area Using matplotlib
        # TODO: Include additional settings to make this look more beautiful
        matplotlib.use("TkAgg")
        self.figure = Figure(figsize=(16, 9))
        self.subplot = self.figure.add_subplot(111)
        self.figure.tight_layout()
        self.xlabel = x_axis_title
        self.ylabel = y_axis_title

        self.terminate = False

        # Sets up the Canvas in which the Figure is displayed, and the Toolbar
        # TODO: Check how these things work in detail and how to make them beautiful
        canvas = FigureCanvasTkAgg(self.figure, self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, self.root)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def __call__(self) -> None:
        """
        Opens the popup window with the live plot.
        Blocks the main thread – after execution of this function, it can only be terminated from other threads.
        """
        _ = animation.FuncAnimation(self.figure, lambda x: None, interval=self.refresh_time)
        self.check_for_termination()
        self.root.mainloop()

    def check_for_termination(self) -> None:
        """
        Loop to be run every second (1000 ms). Destroys the root if the terminate attribute has been set to True.
        """
        if self.terminate:
            self.root.destroy()
            return

        self.root.after(1000, self.check_for_termination)

    def update_plot(self, x_values: np.array, y_values: np.array) -> None:
        """
        Public method to update the data that is plotted in the main window.

        Args:
            x_values: 1D Numpy array of x values to plot
            y_values: 1D Numpy array of y values to plot
        """
        self.subplot.clear()
        self.subplot.set_xlabel(self.xlabel)
        self.subplot.set_ylabel(self.ylabel)
        self.subplot.plot(x_values, y_values)
        self.figure.tight_layout()

    def close_plot(self):
        """
        Public method to be called for closing the TK window.
        """
        self.terminate = True


class ThreadWithReturn(threading.Thread):
    """
    Threading object that returns the return value of the target function upon calling the join() method.
    """

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        """
        Constructor of the ThreadWithReturn class. Calls the constructor of the threading.Thread class.
        Sets the attribute _return to None.

        Args [from threading.Thread documentation]:
            group: Should be None; reserved for future extension when a ThreadGroup class is implemented.
            target: Callable object to be invoked by the run() method. Defaults to None, meaning nothing is called.
            name: Thread name. By default, a unique name is constructed of the form "Thread-N" where N is a small decimal number.
            args: Argument tuple for the target invocation. Defaults to ().
            kwargs: Dictionary of keyword arguments for the target invocation. Defaults to {}.
        """
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self) -> None:
        """
        Re-defines the run() method of threading.Thread.
        Calls and executes the target function, and saves the return value into the _return attribute.
        """
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args) -> Any:
        """
        Re-defines the join() method of threading.Thread.
        Joins the thread into the main thread, and returns the previously saved _return attribute.
        """
        threading.Thread.join(self, *args)
        return self._return
