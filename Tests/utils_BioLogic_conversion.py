import pandas as pd
from matplotlib import pyplot
from galvani import BioLogic

mpr_file = BioLogic.MPRfile("/Users/macbook_m2/PycharmProjects/python_echem/Tests/test_files/RDE4_02_CV_C02.mpr")
df = pd.DataFrame(mpr_file.data)
x = df['control/V']
y= df['I/mA']
pyplot.plot(x,y)
pyplot.show()



