import matplotlib.pyplot as plt
from activeclf.utils.beauty import get_axes
import pandas as pd
import numpy as np

df = pd.read_csv('RoboLab007_GT.csv')

X = df.drop(columns='Phase').to_numpy()
y = df['Phase'].to_numpy()
pdf = np.loadtxt('RoboLab007_GT_pdf.dat')

fig, ax = get_axes(3,3)
ax[0].scatter(*X.T, c=np.array(['r', 'b'])[y], s=1)

ax[1].scatter(*X.T, c=pdf[:,0], cmap='Reds', s=1)

ax[2].scatter(*X.T, c=pdf[:,1], cmap='Blues', s=1)

title_list = [
    'GT labels',
    'GT pdf cl.1',
    'GT pdf cl.2',
        ]

for i in range(3):
    ax[i].set_xlabel('[Lys100]')
    ax[i].set_ylabel('[Asp200]')
    ax[i].set_title(title_list[i])

fig.tight_layout()

plt.show()
