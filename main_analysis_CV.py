from DataAnalyzer.EChemDataAnalyzer import EChemDataAnalyzer
import numpy as np
import pandas as pd

echem_data = EChemDataAnalyzer("CV", np.load(r"C:\Users\Lenovo\Desktop\The Matter Lab\Data\C2COBr2_CV_22-06-23_14-08.pkl",
                                             allow_pickle=True))
integral,peak = echem_data.analyze()


df_int=pd.DataFrame(integral)
df_peak=pd.DataFrame(peak)
df_int.to_csv(r"C:\Users\Lenovo\Desktop\The Matter Lab\Data\int1.csv",index=False)
df_peak.to_csv(r"C:\Users\Lenovo\Desktop\The Matter Lab\Data\peak1.csv",index=False)

