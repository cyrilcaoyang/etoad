from DataAnalyzer.EChemDataAnalyzer import EChemDataAnalyzer
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

path=r"C:\Users\Lenovo\Desktop\The Matter Lab\AutoEChem_Data\SWV"
file_list = os.listdir(path)
data_list=list()
for file in file_list:
    if file.endswith(".pkl"):
        data_list.append(file)

for data_name in data_list:
    data_path = os.path.join(path,data_name)
    data = np.load(data_path, allow_pickle=True)
    if data.shape[1] == 4:
        type = "CV"
        echem_data = EChemDataAnalyzer("CV", data)
        integral, peak = echem_data.analyze()
        #make a directory that store cv data
        cv_path = os.path.join(r"C:\Users\Lenovo\Desktop\The Matter Lab\AutoEChem_Data\CV_analysis",data_name)
        os.mkdir(cv_path)
        fig = plt.figure()
        plt.plot(integral[1:,0],integral[1:,1])
        plt.savefig(os.path.join(cv_path,"integral.png"),dpi=fig.dpi)
        fig = plt.figure()
        plt.plot(data[:, 1], data[:, 2])
        plt.savefig(os.path.join(cv_path, "CV_graph.png"), dpi=fig.dpi)

    if data.shape[1] ==3:
        type="SWV"
        echem_data = EChemDataAnalyzer("SWV", data)
        peak_data_ary = echem_data.analyze()

        fig = plt.figure()
        plt.plot(data[:, 1], data[:, 2])
        for i in peak_data_ary:
            plt.plot(i[0], i[1], "ro")
        plt.savefig(os.path.join(r"C:\Users\Lenovo\Desktop\The Matter Lab\AutoEChem_Data\SWV_analysis",data_name+".png"))




