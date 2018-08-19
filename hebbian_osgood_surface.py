#!/usr/bin/env python
import numpy as np
import numpy.random as rnd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from scipy.linalg import hadamard

def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def normalise(v):
    return v / np.linalg.norm(v)

num_samples_s = 11 # It should be 11 in this script...
num_samples_r = 21 # It should be 21 in this script...

def hebbian_osgood_surfacer(check_list, unit_num, alpha, noise_strength, num_runs, num_samples_s, num_samples_r):
    """
    check_list: 'transfer' or 'retroaction'. They seem identical though...
    unit_num: 2**int. It must be a power of 2. The number of the units.
    alpha: float or int. The weight for the learning.
    noise_strength: float or int. The sd of a gaussian distribution.
    num_runs: int. The number of runs (batches).
    """

    orthog_vs = hadamard(unit_num)[:4]
    s1, r1 = orthog_vs[0], orthog_vs[1]
    s1 = normalise(s1)
    r1 = normalise(r1)

    results = np.zeros((num_samples_s,num_samples_r)) 

    # 1st pair
    W = alpha*np.outer(r1, s1)

    # 2nd pair
    for run in range(num_runs):
        for i in range(num_samples_s):
            for j in range(num_samples_r): 
                gamma_s = i * 0.1
                gamma_r = j * 0.1 - 1.0

                s2 = gamma_s*s1 + (1-gamma_s)*orthog_vs[2]
                s2 = normalise(s2)

                r2 = gamma_r*r1 + (1-gamma_r)*orthog_vs[3]
                r2 = normalise(r2)

                W2 = W + alpha*np.outer(r2, s2) + noise_strength*rnd.randn(unit_num, unit_num)

                if check_list == 'transfer':
                    out = np.dot(W2, s2)
                    results[i][j] += cos_sim(out, r2)

                elif check_list == 'retroaction':
                    out = np.dot(W2, s1)
                    results[i][j] += cos_sim(out, r1)

    results = results/num_runs

    return results

results = hebbian_osgood_surfacer(check_list='transfer', unit_num=2**4, alpha=1,
                                    noise_strength=0.20, num_runs=5000,
                                    num_samples_s=num_samples_s, num_samples_r=num_samples_r)


# Visualising
x = np.linspace(-1,1,num_samples_r)
y = np.linspace(0,1,num_samples_s)
X, Y = np.meshgrid(x, y)

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_xlabel("Response")
ax.set_ylabel("Stimulus")
ax.set_zlabel("Accuracy")

value_for_color = (results - results.min()) / (results.max() - results.min())
colors = cm.magma(value_for_color)
surf = ax.plot_surface(X, Y, results, facecolors=colors, shade=False, rstride=1, cstride=1)
surf.set_facecolor((0,0,0,0))
ax.set_zlim(zmax=1.0)
ax.view_init(20,120)
plt.show()
