# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 14:30:28 2020

@author: roksa
"""

from gurobipy import *
from math import *
import random

config = input("choose a network configuration: ")  # choose one of the these : random, 2a, 2b
n = int(input("Enter Total Number of Users: "))     # total number of users, enter 4 for config 2a, 2b
cell = int(n/2)                                     # number of cellular users
d2d = int(n/2)                                      # number of d2d users
rb = int(n/2)                                       # number of resource blocks
b = 1                                               # number of base station

# Defining coordinates for users

bc = (0,0)  #assuming the position of base station at the center

if config == 'random':
    
    cellc = []  # taking empty array
    for i in range(cell):
        cellc.append((random.randint(-80, 80 ), random.randint(-80, 80)))                                #taking random location
    
    d2dtc = []                         
    for i in range(d2d):                 
        d2dtc.append((random.randint(-80, 80), random.randint(-80, 80)))                                 # taking the position of d2d transmitter wrt base station
    
    d2drc = []  
    for i in range(d2d):                 
        d2drc.append((d2dtc[i][0] + random.randint(-10, 10), d2dtc[i][1] + random.randint(-10, 10)))    # taking the position of d2d receiver wrt base station

if config == '2a':
    
    
    cellc = [(-50, -40), (50, -40)]            # Coordinates of cellular users w.r.t base station
    
    
    d2dtc = [(-50, 40), (50, 40)]              # Coordinates of d2d transmitters w.r.t base station
    
    
    d2drc = [(-50, 50), (50, 50)]              # Coordinates of d2d receivers w.r.t base station
    
if config == '2b':
    
    
    cellc = [(-50, -40), (50, 40)]              # C2doordinates of cellular users w.r.t base station
    
    
    d2dtc = [(-50, 40), (50, -40)]             # Coordinates of d2d transmitters w.r.t base station
    
    
    d2drc = [(-50, 50), (50, -50)]            # Coordinates of d2d receivers w.r.t base station
    

# Model
m = Model("Current_Network")

# Defining objective functions
x1 = tupledict()
for i in range(rb):
    for j in range(cell):
        x1[i, j] = m.addVar(vtype=GRB.BINARY, name="rb" + str(i) + " is used by cell" + str(j))

x2 = tupledict()
for i in range(rb):
    for j in range(d2d):
        x2[i, j] = m.addVar(vtype=GRB.BINARY, name="rb" + str(i) + " is used by d2d" + str(j))

x3 = tupledict()
for i in range(rb):
    for j in range(cell):
        for k in range(d2d):
            x3[i, j, k] = m.addVar(vtype=GRB.BINARY, name="rb" + str(i) + " is shared by cell" + str(j) + " d2d" + str(k))

x4 = tupledict()
for i in range(rb):
    for j in range(d2d):
        for k in range(j, d2d):
            if j != k:
                x4[i, j, k] = m.addVar(vtype=GRB.BINARY, name="rb" + str(i) + " is shared by d2d" + str(j) + " d2d" + str(k))

# Distances calculation using euclidean formula
b_d2d = tupledict()
d2d_cell = tupledict()
d2d_d2d = tupledict() 

for i in range(d2d):
    b_d2d[i] = sqrt(pow(bc[0] - d2dtc[i][0], 2)+pow(bc[1] - d2dtc[i][1], 2))

for i in range(cell):
    for j in range(d2d):
       d2d_cell[i, j] = sqrt(pow(d2drc[j][0] - cellc[i][0], 2) + pow(d2drc[j][1] - cellc[i][1], 2))

for i in range(d2d):
    for j in range(i, d2d):
        if i != j:
            d2d_d2d[i, j] = sqrt(pow(d2drc[j][0] - d2dtc[i][0], 2) + pow(d2drc[j][1] - d2dtc[i][1], 2))

#FSPL and Interference calculation

FSPL_b_d2d = tupledict()
FSPL_d2d_cell = tupledict()
FSPL_d2d_d2d = tupledict()
Infr_b_d2d = tupledict()
Infr_d2d_cell = tupledict()
Infr_d2d_d2d = tupledict()

for i in range(d2d):
   FSPL_b_d2d[i] = 20*log((b_d2d[i])/1000, 10) + 20*log(2, 10) + 92.45    #calculating the FSPL of base station
   Infr_b_d2d[i] = 26 - FSPL_b_d2d[i]                                                #calculating interference of base station due to d2d transmitter
   
for i in range(cell):
    for j in range(d2d):
            FSPL_d2d_cell[i, j] = 20*log((d2d_cell[i, j])/1000, 10) + 20*log(2, 10) + 92.45    #calculating the FSPL of d2d receiver
            Infr_d2d_cell[i, j] = 26 - FSPL_d2d_cell[(i, j)]                                #calculating interference of d2d receiver due to cellular user
            
for i in range(d2d):
    for j in range(i, d2d):
        if i != j:
            FSPL_d2d_d2d[i, j] = 20*log((d2d_d2d[i, j])/1000, 10) + 20*log(2, 10) + 92.45    #calculating the FSPL of d2d receiver
            Infr_d2d_d2d[i, j] = 26 - FSPL_d2d_d2d[(i, j)]                                  #calculating interference of one d2d receiver due to another d2d transmitter

# Total interference calculation
a = b = c = 0   
obj = 0

for i in range(rb):
    for j in range(cell):
        for k in range(d2d):
                a = a + Infr_b_d2d[k] * x3[i, j, k]
    for j in range(cell):
        for k in range(d2d):
                b = b + Infr_d2d_cell[(j, k)] * x3[i, j, k]
    for j in range(d2d):
        for k in range(j, d2d):
            if j != k:
                c = c + Infr_d2d_d2d[(j, k)] * x4[i, j, k]

obj = a + b + c  #total interference

# Minimizing the interference
m.setObjective(obj, GRB.MINIMIZE)

#Defining constraints          
for c in range(cell):
    m.addConstr(sum(x1[(i, c)] for i in range(rb)) >= 1)       #every cell should have 1 resource block

for d in range(d2d):
    m.addConstr(sum(x2[(i, d)] for i in range(rb)) >= 1)       #every d2d should have 1 resource block

for r in range(rb):
    m.addConstr(sum(x1[(r, i)] for i in range(cell)) <= 1)     #no two cellular should share same resource block
    m.addConstr(sum(x1[(r, i)] for i in range(cell)) + sum(x2[(r, j)] for j in range(d2d)) <= 2)     #cellular user and d2d user can share same resource block
    m.addConstr(sum(x2[(r, i)] for i in range(d2d)) + sum(x2[(r, j)] for j in range(d2d) if i != j) <= 2)   #two different d2d pairs can share same resource block
#constraints for conversion from non-linear to linear using product variable method 
for r in range(rb):
    for c in range(cell):
        for d in range(d2d):
            m.addConstr((x3[(r, c, d)] <= x1[(r, c)]))         
            m.addConstr((x3[(r, c, d)] <= x2[(r, d)]))
            m.addConstr((x3[(r, c, d)] >= x1[(r, c)] + x2[(r, d)] - 1))

for r in range(rb):
    for i in range(d2d):
        for j in range(i, d2d):
            if i != j:
                m.addConstr((x4[(r, i, j)] <= x2[(r, i)]))     
                m.addConstr((x4[(r, i, j)] <= x2[(r, j)]))
                m.addConstr((x4[(r, i, j)] >= x2[(r, i)] + x2[(r, j)] - 1))
                
#Calling the gurobi optimization function
m.optimize()

# Printing the Solution
print('\n------------------------------RESULTS-----------------------------------\n')

print('Cellular Coordinates')
print(cellc)
print('D2D transmitters Coordinates')
print(d2dtc)
print('D2D Receivers Coordinates')
print(d2drc)
print("\nMinimum Interference (Objective): " + str(round(m.objVal, 2)) + 'dBm')


#printing the shared and used resources after optimization
m.printAttr('x')
     
#showing result for all variables
# for v in m.getVars():
#     print('%s %g' % (v.varName, v.x))