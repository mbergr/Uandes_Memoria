# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 19:21:16 2020

@author: mathi
"""


import glob
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import Model, GRB, quicksum


#variable global ft
global ft
ft=[]

#funcion que guarda los tiempos en que se encuentran las soluciones factibles en la variable global
def mycallback(model, where):
    if where == GRB.Callback.MIPSOL:
        ft.append(model.cbGet(GRB.Callback.RUNTIME))
      

def read_param(infile):
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
            clients=elements[0]
            m=elements[1]
            Q=elements[2]
        else:
            elements=list(map(float,line.split()))
            V.append(int(elements[0]))
            xc.append(elements[1])
            yc.append(elements[2])      
            u_l.append(elements[3])
            q_l.append(elements[4])
            e_l.append(elements[5])
            l_l.append(elements[6])
        i+=1    
        
    vehicles=(clients//5)-1
    
    N=V[:clients]
    D=V[clients:]
    A=[(i,j) for i in V for j in V if i!=j] #set A
    
    R=[i for i in range(1,vehicles+1)] #set R
    c={(i,j): np.hypot(xc[i-1]-xc[j-1],yc[i-1]-yc[j-1]) for i,j in A} #distance between nodes
    M=sum(c.values()) #big M for constrains (7)   
    #se crean diccionarios para que correspondan los indices con la posicion de la lista
    u= {i: u_l[i-1] for i in V} #unloading time
    q= {i: q_l[i-1] for i in V} #demand
    e= {i: e_l[i-1] for i in V} #early time window
    l= {i: l_l[i-1] for i in V} #late time window
    M=sum(c.values())+sum(u.values())
    return N, D, A, R, M, u, q, e, l, vehicles, m, clients, Q, V, c
    
def optimize(parameter, obj):   
    global ft   
    N=parameter[0]
    D=parameter[1]
    A=parameter[2]
    R=parameter[3]
    M=parameter[4]
    u=parameter[5]
    q=parameter[6]
    e=parameter[7]
    l=parameter[8]
    vehicles=parameter[9]
    m=parameter[10]
    clients=parameter[11]
    Q=parameter[12]
    V=parameter[13]
    c=parameter[14]   
    n=clients
    
    #model in gurobipy  
    mdl = Model("MD-CCVRPTW")
    
    x=mdl.addVars(V,V,R, vtype=GRB.BINARY) #X variable
    t=mdl.addVars(V,R, vtype=GRB.CONTINUOUS) #t variable
    
    if obj==1:
        mdl.modelSense=GRB.MINIMIZE
        mdl.setObjective(quicksum(t[i,k] for i in N for k in R)) #objective function 1
    elif obj==2:
        mdl.modelSense=GRB.MINIMIZE
        mdl.setObjective(quicksum(t[i,k]-e[i] for i in N for k in R)) #objective function 2
    elif obj==3:
        mdl.modelSense=GRB.MAXIMIZE
        mdl.setObjective(quicksum(l[i]-t[i,k] for i in N for k in R)) #objective function 3
    elif obj==4:
        mdl.modelSense=GRB.MINIMIZE
        mdl.setObjective((1/n)*quicksum((t[i,k]-e[i])/(l[i]-e[i]) for i in N for k in R)) #objective function 4
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
    
    #mdl.Params.MIPGap= 0.1
    mdl.Params.Timelimit = 3600
    mdl.Params.SolFiles
    first_sol='Not Found'
    
    try:
        mdl.optimize(mycallback)
        if len(ft)>0:
            first_sol=min(ft)
        #print(ft,first_sol)
        ft=[]
        
        
        obj = mdl.getObjective()
        sol=[]
        
        for i in V:
            for j in V:
                for k in R:
                    if x[i,j,k].x>0.7:
                        s="x[{},{},{}]={}, t[{},{}]={}".format(i,j,k,x[i,j,k].x,i,k,t[i,k].x)
                        sol.append(s)
        
        return obj.getValue(), mdl.Runtime, vehicles, clients, m, mdl.MIPGap, first_sol, sol 
    
    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ': ' + str(e))

    except AttributeError:
        print('Encountered an attribute error')
        return ['Not Found', mdl.Runtime, vehicles, clients, m, 'Not Found', first_sol]+[[None]]



txtfiles = []
folder='New_instances_final_2depot2\\'
#folder='small_inst\\'
#folder='cordeau-menosde100\\'
for instance in glob.glob(folder+'*.txt'):
    txtfiles.append(instance)
instances=[]    
objectives=[]
times=[]
vehicles=[]
clients=[]
depots=[]
FO=[]
txtout=[]
gap=[]
fs=[]


for file in txtfiles:
    if file[-10:]=="readme.txt":
        continue
    infile = open(file)
    print(file)
    parameters=read_param(infile) 
    for obj in range(1,5):    
        L=optimize(parameters, obj)
        
        short_file=file.replace(folder,'')
        short_file=short_file.replace('.txt','')
        instances.append(short_file)   
        objectives.append(L[0])
        times.append(L[1])
        vehicles.append(L[2])
        clients.append(L[3])
        depots.append(L[4])
        gap.append(L[5])
        fs.append(L[6])
        FO.append(obj)
        d={'FO':FO, 'Instance':instances, 'Clientes':clients, 'Depositos':depots, 
           'Vehiculos':vehicles, 'Objective': objectives,'Gap':gap, 'First Sol':fs,'Time': times}
        df = pd.DataFrame(data=d)
        df.to_excel("Output.xlsx", index=False)
        txtout=txtout+["Objetivo: "+str(L[0]),"Tiempo: "+str(L[1]),"Vehiculos: "+str(L[2]),
                       "Clientes: "+str(L[3]),"Depositos: "+str(L[4])]
        txtout=txtout+L[7]
        with open('Output\Output_'+short_file+'_obj'+str(obj)+'.txt', 'w') as f:
            for item in txtout:
                f.write("%s\n" % item) 
        f.close()
        txtout=[]
    infile.close()

"""
for file in txtfiles:
    if file[-10:]=="readme.txt":
        continue
    infile = open(file)
    print(file)
    parameters=read_param(infile) 
    obj=2
    L=optimize(parameters, obj)
    
    short_file=file.replace(folder,'')
    short_file=short_file.replace('.txt','')
    instances.append(short_file)   
    objectives.append(L[0])
    times.append(L[1])
    vehicles.append(L[2])
    clients.append(L[3])
    depots.append(L[4])
    gap.append(L[5])
    fs.append(L[6])
    FO.append(obj)
    d={'FO':FO, 'Instance':instances, 'Clientes':clients, 'Depositos':depots, 
       'Vehiculos':vehicles, 'Objective': objectives,'Gap':gap, 'First Sol':fs,'Time': times}
    df = pd.DataFrame(data=d)
    df.to_excel("Output.xlsx", index=False)
    txtout=txtout+["Objetivo: "+str(L[0]),"Tiempo: "+str(L[1]),"Vehiculos: "+str(L[2]),
                   "Clientes: "+str(L[3]),"Depositos: "+str(L[4])]
    txtout=txtout+L[7]
    with open('Output\Output_'+short_file+'_obj'+str(obj)+'.txt', 'w') as f:
        for item in txtout:
            f.write("%s\n" % item) 
    f.close()
    txtout=[]
    infile.close()
"""