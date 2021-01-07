# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 10:19:55 2020

@author: mathi
"""

import numpy as np
import matplotlib.pyplot as plt
import itertools

#instance reading
infile = open('New_instances_final/20x4_1.txt')

V=[] #nodos
xc=[] #x coordinate
yc=[] #y coordinate
u_l=[] #unloading time
q_l=[] #demand
e_l=[] #beginig of the window
l_l=[] #end of the time window
i=0
for line in infile:
    #print("i={}".format(i))
    if i==0:
        elements=list(map(int,line.split()))
        vehicles=elements[1] #vehiculos
        clients=elements[2] #clientes
        m=elements[3] #depots
        #print("vehicles={}, clientes={}, depots={}".format(vehicles, clientes, m))
    elif i<=m:
        elements=list(map(int,line.split()))
        Q=elements[1] #capacidad
    elif i<=clients+m:
        elements=list(map(float,line.split()))
        #print(len(elements))
        V.append(int(elements[0]))
        xc.append(elements[1])
        yc.append(elements[2])
        u_l.append(elements[3])
        q_l.append(elements[4])
        a=int(elements[6])
        e_l.append(elements[7+a])
        l_l.append(elements[7+a+1])
    else:
        #print(i,clients,line)
        elements=list(map(float,line.split()))
        V.append(int(elements[0]))
        xc.append(elements[1])
        yc.append(elements[2])      
        u_l.append(elements[3])
        q_l.append(elements[4])
        e_l.append(elements[7])
        l_l.append(elements[8])
    i+=1    
#print("sum(u_l)={}, vehicles*Q".format(sum(q_l)))
#print(q_l)
n=clients
#print(len(q_l))
#N=[i for i in range(1, clients+1)] #set N
#D=[i for i in range(clients+1, nodes+1)] #set D
N=V[:clients]
D=V[clients:]
#print("V={}, N={}, D={}".format(V,N,D)) #set V
#print("e_l={}, \nl_l={}".format(e_l,l_l))

A=[(i,j) for i in V for j in V if i!=j] #set A
vehicles=(vehicles)*m
#print(vehicles)
#vehicles=72
#print("sum(q_l)={}, vehicles*Q={}".format(sum(q_l),vehicles*Q))

R=[i for i in range(1,vehicles+1)] #set R
c={(i,j): np.hypot(xc[i-1]-xc[j-1],yc[i-1]-yc[j-1]) for i,j in A} #distance between nodes


#print("c={}".format(c))
#M=max(c.values()) #big M for constrains (7) --> NOT BIG ENOUGH
#M=99999999999999999999999999999999999999999999
M=sum(c.values())#big M for constrains (7)


#se crean diccionarios para que correspondan los indices con la posicion de la lista
u= {i: u_l[i-1] for i in V} #unloading time
#print("u={}".format(u))
q= {i: q_l[i-1] for i in V} #demand
e= {i: e_l[i-1] for i in V} #early time window
l= {i: l_l[i-1] for i in V} #late time window

#model in gurobipy
from gurobipy import Model, GRB, quicksum

mdl = Model("MD-CCVRPTW")

x=mdl.addVars(V,V,R, vtype=GRB.BINARY) #X variable
t=mdl.addVars(V,R, vtype=GRB.CONTINUOUS) #t variable
mdl.modelSense=GRB.MINIMIZE
#mdl.setObjective(quicksum(t[i,k] for i in N for k in R)) #objective function
mdl.setObjective(quicksum(t[i,k]-e[i] for i in N for k in R)) #objective function
#mdl.setObjective(quicksum(l[i]-t[i,k] for i in N for k in R)) #objective function
#mdl.setObjective((1/n)*quicksum((t[i,k]-e[i])/(l[i]-e[i]) for i in N for k in R)) #objective function
#restrictions


mdl.addConstrs(quicksum(x[i,j,k] for i in V for k in R if i!=j)==1 for j in N) #(2)
mdl.addConstrs((quicksum(x[i,j,k] for i in V if i!=j)-quicksum(x[j,i,k] for i in V if i!=j))==0 for j in N for k in R) #(3)
mdl.addConstrs(quicksum(x[i,j,k] for i in D for j in V)==1 for k in R) #(4)
mdl.addConstrs(quicksum(x[j,i,k] for i in D for j in V)==1 for k in R) #(5)
mdl.addConstrs(quicksum(q[j]*x[i,j,k] for i in V for j in V if i!=j)<=Q for k in R) #(6)
#mdl.addConstrs(t[i,k]+c[i,j]+u[i]-t[j,k]<=(1-x[i,j,k])*M for i in V for j in N for k in R if i!=j) #(7) NUEVA
mdl.addConstrs((x[i,j,k]==1) >> (t[i,k]+c[i,j]+u[i]-t[j,k]<=0) for i in V for j in N for k in R if i!=j) #(7) NUEVA
mdl.addConstrs(e[i]<=t[i,k] for i in V for k in R) #(8) NUEVA
mdl.addConstrs(t[i,k]+u[i]<=l[i] for i in V for k in R) #(9) NUEVA
mdl.addConstrs(t[i,k]>=0 for i in V for k in R)


mdl.Params.MIPGap= 0.1
#mdl.Params.NumericFocus=3
#mdl.Params.Timelimit = 30

mdl.optimize()

active_arcs=[(i,j) for i in V for j in V for k in R if x[i,j,k].x>0.9]

print("\nParameters:\nDepots={}, Clients={}, Vehicles={}".format(m,clients,vehicles))
print("\nx[i,j,k], t[i,k]  donde i,j: nodos; k: vehiculo\n")

#print solution
Sol_matrix={}
for i in V:
    for j in V:
        for k in R:
            #if x[i,j,k].x>0.7:
                #Sol_matrix[(i,k)]=t[i,k].x
                    #print("e[{}]={}, l[{}]={}".format(i,e[i],i,l[i]))
                    #print("c[{},{}]={}, u[{}]={}".format(i,j,c[i,j],i,u[i]))
            print("x[{},{},{}]={}, t[{},{}]={}".format(i,j,k,x[i,j,k].x,i,k,t[i,k].x))
                #print("e={} < t={} < l={} ; u={}".format(e[i],t[i,k].x,l[i],u[i])) #esta tomando los valores early
#print(Sol_matrix)
#plot nodes


for i in V:    
    plt.annotate("Node_{}".format(i),(xc[i-1],yc[i-1])).set_fontsize(3)

colors = itertools.cycle(["r", "b", "g", "c", "m", "y", "k"])

#plot active arcs
#for i,j in active_arcs:    
#    plt.plot([xc[i-1],xc[j-1]],[yc[i-1],yc[j-1]],c=next(colors), linewidth=.85)

for k in R:
    prox_color=next(colors)
    for i in V:
        for j in V:
            if x[i,j,k].x>0.9:
                plt.plot([xc[i-1],xc[j-1]],[yc[i-1],yc[j-1]],c=prox_color, linewidth=.45, zorder=1)
                #plt.annotate("k={}".format(k),((xc[j-1]+xc[i-1])/2,(yc[j-1]+yc[i-1])/2)).set_fontsize(4)

plt.scatter(xc[0:clients], yc[0:clients],c='b', s=3, zorder=2)
plt.scatter(xc[clients:], yc[clients:],c='r', s=3, zorder=2)
#plt.figure(figsize=(10, 10), dpi=80)
plt.axis('auto')
#fig.suptitle('test title', fontsize=20)

#plt.savefig("test.png")
plt.rcParams.update({'font.size': 4})
plt.savefig('foo.png', dpi=400, bbox_inches=0)

plt.show()
print(D)






