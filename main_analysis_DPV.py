from DataAnalyzer.EChemDataAnalyzer import EChemDataAnalyzer
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = np.load(r"C:\Users\Lenovo\Desktop\The Matter Lab\Test_Data\Data\DiquatC2_DPV.pkl",
                                             allow_pickle=True)
echem_data = EChemDataAnalyzer("DPV", data)
peak_data_ary = echem_data.analyze()

#plot the result
fig=plt.figure()
plt.plot(data[:,1],data[:,2])
for i in peak_data_ary:
    plt.plot(i[0],i[1],"ro")
fig.savefig(r"C:\Users\Lenovo\Desktop\The Matter Lab\Test_Data\Data\test.png",dpi=fig.dpi)

