import matplotlib.pyplot as plt
import numpy as np

x = np.loadtxt('20210923_simona_t1.txt')[:,-4]
#x_mean_removed = x - x.mean()
mv = x/1024./1.1*3.3-1.5
plt.plot(mv, 'k')
plt.ylabel('mV')
plt.xlabel('t (ms)')
plt.show()
