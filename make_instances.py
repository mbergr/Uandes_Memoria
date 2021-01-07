# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:06:09 2020

@author: mathi
"""

from random import sample

#PARAMETROS
#cantidad de clientes requeridos
n=30
#archivo
short_file='pr20'



def comprehension(a, b):
     return [x for x in a if x not in b]



infile = open('cordeau-al-2001-mdvrptw\\'+short_file+'.txt')


#primera linea de lista original
first_line=[]
#lista de clientes
L=[]
#lista de depositos
L_depot=[]




i=0
for line in infile:
    #print("i={}".format(i))
    if i==0:
        elements=list(map(int,line.split()))
        vehicles=elements[1] #vehiculos
        clients=elements[2] #clientes
        m=elements[3] #depots
        first_line.extend([clients, m])
        #print("vehicles={}, clientes={}, depots={}".format(vehicles, clientes, m))
    elif i<=m:
        elements=list(map(int,line.split()))
        Q=elements[1] #capacidad
        if len(first_line)==2:
            first_line.append(Q)
    elif i<=clients+m:
        elements=list(map(float,line.split()))

        j=(int(elements[0]))
        x=(elements[1])
        y=(elements[2])
        u=(elements[3])
        q=(elements[4])
        a=int(elements[6])
        e=(elements[7+a])
        l=(elements[7+a+1])
        
        L.append([j,x,y,u,q,e,l])
        
    else:
        #print(i,clients,line)
        elements=list(map(float,line.split()))
               
        j=(int(elements[0]))
        x=(elements[1])
        y=(elements[2])      
        u=(elements[3])
        q=(elements[4])
        e=(elements[7])
        l=(elements[8])
        
        L_depot.append([j,x,y,u,q,e,l])
        
    i+=1    
        



first_line[0]=n

for k in range(1,3):
    txtout=[]
    new_list=sample(L,n)
    
    new_list_depot=sample(L_depot,first_line[1])
    L=comprehension(L,new_list)
    
    primera_linea=' '.join(list(map(str,first_line)))
    #print(primera_linea)
    txtout+=[primera_linea]
    i=1
    for e in new_list:
        e[0]=i 
        linea=' '.join(list(map(str,e)))
        txtout+=[linea]
        i+=1
        #print(linea)
    for e in new_list_depot:
        e[0]=i
        linea=' '.join(list(map(str,e)))
        txtout+=[linea]
        i+=1
    with open('New_instances\\'+short_file+'_'+str(first_line[0])+'x'+str(first_line[1])+'_'+str(k)+'.txt', 'w') as f:
        for item in txtout:
            f.write("%s\n" % item) 
        