# -*- coding: utf-8 -*-
"""
Created on Sat May  1 16:09:02 2021

@author: charl
"""
from scipy import optimize as sc
import numpy as np
import pylab as pl
from random import random

voltage = list("""53.1
53.2
53.3
53.6
54.1
54.6
55.1
55.6
56.1
56.6
57.1
57.7""".replace('\n',',').split(','))

voltage2 = []

gain = list("""440851
532972
627607
864029
1302979
1662700
2153865
2492391
2916410
3329418
3554240
4232896""".replace('\n',',').split(','))
gain2 = []


fitted = list("""456737.6092
535838.9377
614940.2662
852244.2515
1247750.894
1643257.536
2038764.178
2434270.821
2829777.463
3225284.105
3620790.747
4095398.718""".replace('\n',',').split(','))

fitted2 = []


rpower = list("""0.0187877
0.268509082
0.145424849
0.20677238
0.200914736
0.188125106
0.350181455
0.260243683
0.191860087
0.40210022
0.435849763
0.089856569""".replace('\n',',').split(','))

rpower2 = []



for row in voltage:
    voltage2.append(float(row))
    
for row in gain:
    gain2.append(float(row))

for row in fitted:
    fitted2.append(float(row))
    
for row in rpower:
    rpower2.append(float(row))    
    
    
def stright_line(x,m,c):
    y = (m*x) + c
    return y 
popt_sl, covp_sl = sc.curve_fit(stright_line,voltage2,gain2)
print(popt_sl)
print(np.sqrt(np.diag(covp_sl)))
x = np.linspace(40,70,1000)
y = np.zeros((1000))
pl.ylim(-.8e6,5e6)
pl.xlim(51,58)
pl.xlabel('Bias Voltage [V]')
pl.ylabel('Gain')
pl.title('Gain against Bias Voltage')
pl.axhline(0,color='black')
pl.plot(voltage2,gain2,'+',label = "Data")
#pl.plot(voltage2,fitted2,label = "Fit", color = 'red')
pl.plot(x,stright_line(x,*popt_sl),label = "Fit", color = 'red')
pl.legend()
pl.rcParams['figure.figsize']  = 16,9
pl.savefig('Saved/fig0.png')


pl.rcParams.update({'font.size': 20})

pl.show()


datax = []
datay = []


with open("staircase1.txt") as infile:
    ob = infile.readlines()
    for index,line in enumerate(ob):
        if index <= 45:
            
            row = list(line.split())
            datax.append(-float(row[0]))
            datay.append(float(row[1]))
pl.xlabel('Threshold [mV]')
pl.gca().invert_xaxis()
pl.ylabel('DCR [Hz]')
pl.title('DCR Stair Case')
pl.plot(datax,datay,'+',label = "Data")
pl.yscale('log')
pl.legend()
pl.rcParams['figure.figsize']  = 16,9
pl.savefig('Saved/fig0.png')


pl.rcParams.update({'font.size': 20})

pl.show()
datax = []
datay = []

with open("staircase2.txt") as infile:
    ob = infile.readlines()
    for index,line in enumerate(ob):
        if index <= 136:
            
            row = list(line.split())
            datax.append(-float(row[0]))
            datay.append(float(row[1]))
pl.xlabel('Threshold [mV]')
pl.gca().invert_xaxis()
pl.ylabel('DCR [Hz]')
pl.title('DCR Stair Case')
pl.plot(datax,datay,'+',label = "Data")
pl.yscale('log')
pl.legend()
pl.rcParams['figure.figsize']  = 16,9
pl.savefig('Saved/fig0.png')


pl.rcParams.update({'font.size': 20})

pl.show()

            
def x_fit(x):
    return (15-(.5*(x-56)**2))

voltage2 = np.array(voltage2)
print(voltage2)
x = np.linspace(40,70,1000)

pl.xlabel('Bias [V]')
pl.xlim(50,60)
pl.ylabel('R')
pl.title('Resolution Power')
pl.ylim(0,20)
pl.plot(x,x_fit(x),'--',color = 'red')
pl.scatter(voltage2,x_fit(voltage2),s = 100)
pl.rcParams['figure.figsize']  = 16,9
pl.rcParams.update({'font.size': 20})
pl.show()








def x_squ(x,c,yi,a):
    return a*((x-c)**2) + yi

popt_sl, covp_sl = sc.curve_fit(x_squ,voltage2,rpower2)
print(popt_sl)
print(np.sqrt(np.diag(covp_sl)))

pl.xlabel('Bias [V]')
pl.xlim(50,65)
pl.ylim(-1,1)
pl.ylabel('R')
pl.title('Resolution Power')

pl.plot(voltage2,rpower2,'+')
pl.plot(x,x_squ(x,*popt_sl),'--',color = 'red')
pl.rcParams['figure.figsize']  = 16,9
pl.rcParams.update({'font.size': 20})
pl.show()
first = """
1
Digitizer
ch.0:  FALSE 	 ch.1:  TRUE 	 DC offset 0: 0 	 DC offset 1: -6 	 act ch:  1 	trig mode:  TRUE 	 rise time:  8 	 trig mean:  8 	 trig thr 0:  30 	 trig thr 1:  10 	gate mode:  FALSE 	 gate width:  504 	 pre gate:  48 	 holdoff:  504 	bsln mean:  16 	 bsln thr:  8 	 noflattime:  512 	GPO:  2 	 coinc:  FALSE 	 coinc time:  0 
PSAU
ch.0:  FALSE 	 ch.1:  TRUE 	 Vset 0:  30.900000 	 Vset 1:  55.599998 	 Gain0:  32 	 Gain1:  32 	 comp0:  FALSE 	 comp1:  TRUE 	 thr0:  -14.000000 	 thr1:  -15.000000 	 width0:  110 	 width1:  110 	 DOUT0:  FALSE 	 DOUT1:  TRUE 	 outputlevel:  TTL 	 coinc:  FALSE 	 coinc time:  20 

Vmon 0:  0.000000 	 Vmon 1:  55.509998 	 Temp 0:  21.000000 	 Temp 1:  25.000000 	 Temp board:  26.700001 
"""



second = """
2
Digitizer
ch.0:  FALSE 	 ch.1:  TRUE 	 DC offset 0: 0 	 DC offset 1: -6 	 act ch:  1 	trig mode:  TRUE 	 rise time:  8 	 trig mean:  8 	 trig thr 0:  30 	 trig thr 1:  10 	gate mode:  FALSE 	 gate width:  504 	 pre gate:  48 	 holdoff:  504 	bsln mean:  16 	 bsln thr:  8 	 noflattime:  512 	GPO:  2 	 coinc:  FALSE 	 coinc time:  0 
PSAU
ch.0:  FALSE 	 ch.1:  TRUE 	 Vset 0:  30.900000 	 Vset 1:  55.599998 	 Gain0:  32 	 Gain1:  32 	 comp0:  FALSE 	 comp1:  TRUE 	 thr0:  -14.000000 	 thr1:  -15.000000 	 width0:  110 	 width1:  110 	 DOUT0:  FALSE 	 DOUT1:  TRUE 	 outputlevel:  TTL 	 coinc:  FALSE 	 coinc time:  20 

Vmon 0:  0.000000 	 Vmon 1:  55.509998 	 Temp 0:  21.100000 	 Temp 1:  25.000000 	 Temp board:  26.700001 



"""

for i in range(0,len(first)-1):
    if first[i] != second[i]:
        print(first[:i])
        
        
#fake stair case plot

x = []
y = []

for i in range(1,100):
    x.append(-i)

    num = 10**(int((100-i)/20) + .1*random())
    y.append(num)



for num in (20,40,60,80):
    for i in (num-3,num-2,num-1):
        y[i] = y[i]/(10*random())
        
        
        
pl.xlabel('Threshold [mV]')
pl.gca().invert_xaxis()
pl.ylabel('DCR [Hz]')
pl.title('DCR Stair Case')
pl.plot(x,y,'+',label = "Data")
pl.yscale('log')
pl.legend()
pl.rcParams['figure.figsize']  = 16,9