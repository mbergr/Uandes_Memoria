

import numpy as np
import matplotlib.pyplot as plt
rnd = np.random

#instance reading
infile = open('10x4-1.txt')

i=0
xc=[]
yc=[]
q_l=[]
for line in infile.readlines():
    if i==0:
        clients=int(line) #clients
    elif i==1:
        m=int(line) #depots
    elif i==2:
        Q=int(line) #capacity
    else:
        l=list(map(float,line.split()))
        if len(l)==2:
            xc.append(int(l[0])) #x coordenate
            yc.append(int(l[1])) #y coordenate
        if len(l)==1:
            q_l.append(int(l[0])) #demand
    i+=1

nodes=m+clients #total nodes
vehicles=5 #vehicles number set to 5

N=[i for i in range(1, clients+1)] #set N
D=[i for i in range(clients+1, nodes+1)] #set D
V=D+N #set V
A=[(i,j) for i in V for j in V if i!=j] #set A

R=[i for i in range(1,vehicles+1)] #set R
c={(i,j): np.hypot(xc[i-1]-xc[j-1],yc[i-1]-yc[j-1]) for i,j in A} #distance bettwen nodes

#M=max(c.values()) #big M for constrains (7) --> NOT BIG ENOUGH
M=1000000 #big M for constrains (7)


q= {i: q_l[i-1] for i in V} #demand

#model in gurobipy
from gurobipy import Model, GRB, quicksum

mdl = Model("MD-CCVRP")

x=mdl.addVars(V,V,R, vtype=GRB.BINARY) #X variable
t=mdl.addVars(V,R, vtype=GRB.CONTINUOUS) #t variable
mdl.modelSense=GRB.MINIMIZE
mdl.setObjective(quicksum(t[i,k] for i in N for k in R)) #objective function

#restrictions

mdl.addConstrs(quicksum(x[i,j,k] for i in V for k in R if i!=j)==1 for j in N) #(2)
mdl.addConstrs((quicksum(x[i,j,k] for i in V if i!=j)-quicksum(x[j,i,k] for i in V if i!=j))==0 for j in N for k in R) #(3)
mdl.addConstrs(quicksum(x[i,j,k] for i in D for j in V)==1 for k in R) #(4)
mdl.addConstrs(quicksum(x[j,i,k] for i in D for j in V)==1 for k in R) #(5)
mdl.addConstrs(quicksum(q[j]*x[i,j,k] for i in V for j in V if i!=j)<=Q for k in R) #(6)
mdl.addConstrs(t[i,k]+c[i,j]-t[j,k]<=(1-x[i,j,k])*M for i in V for j in N for k in R if i!=j) #(7)
mdl.addConstrs(t[i,k]>=0 for i in V for k in R) #(8)

#mdl.Params.MIPGap= 0.1
mdl.Params.Timelimit = 30

mdl.optimize()

active_arcs=[(i,j) for i in V for j in V for k in R if x[i,j,k].x>0.9]

print("\nParameters:\nDepots={}, Clients={}, Vehicles={}".format(m,clients,vehicles))
print("\nx[i,j,k], t[i,k]  donde i,j: nodos; k: vehiculo\n")

#print solution
for i in V:
    for j in V:
        for k in R:
            if x[i,j,k].x>0.7:
                print("x[{},{},{}]={}, t[{},{}]={}".format(i,j,k,x[i,j,k].x,i,k,t[i,k].x))


#plot nodes
plt.scatter(xc[0:clients], yc[0:clients],c='b')
plt.scatter(xc[clients:], yc[clients:],c='r')
for i in range(1,nodes+1):    
    plt.annotate("Node_{}".format(i),(xc[i-1],yc[i-1]))   
    
#plot active arcs
for i,j in active_arcs:
    plt.plot([xc[i-1],xc[j-1]],[yc[i-1],yc[j-1]],c='g')
plt.show()
