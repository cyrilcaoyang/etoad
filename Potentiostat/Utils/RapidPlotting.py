import matplotlib.pyplot as plt
import numpy as np

def scatter_plot(x_values: np.array, y_values: np.array):
    """
    Crude matplotlib scatter plot to visualize the results and see if the measurement was somewhat successful.

    Args:
        x_values: Numpy array of the x values of all data points
        y_values: Numpy array of the y values of all data points
    """
    plt.scatter(x_values, y_values)
    plt.show()
