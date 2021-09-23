import matplotlib.pyplot as plt
import numpy as np

x = np.loadtxt('20210923_simona_t1.txt')[:,-4]
mv = x/1024./1.1*3.3-1.5
plt.plot(mv, 'k')
plt.ylim([-1.5,1.5])
plt.ylabel('mV')
plt.xlabel('t (ms)')
plt.show()
