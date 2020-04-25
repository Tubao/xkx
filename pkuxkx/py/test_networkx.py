# -*- coding: utf-8 -*-
#%%

import networkx as nx

import numpy as np
import matplotlib.pyplot as plt
from mydb import getconn
import re
import math
from collections import defaultdict
#%%

def CalDistance(e1,e2):
    return math.sqrt((e1[0]-e2[0])*(e1[0]-e2[0]) + (e1[1]-e2[1])*(e1[1]-e2[1]))
G = nx.DiGraph()
""" G.add_edges_from(
    [('A', 'B'), ('B', 'A'), ('A', 'C'), ('D', 'B'), ('E', 'C'), ('E', 'F'),
     ('B', 'H'), ('B', 'G'), ('B', 'F'), ('C', 'G')])
G.add_edge('J', 'K',action="north")
G.add_edge('K', 'J',action="south")

val_map = {'A': 1.0,
           'D': 0.5714285714285714,
           'H': 0.0}

values = [val_map.get(node, 0.25) for node in G.nodes()]

# Specify the edges you want here
red_edges = [('A', 'C'), ('E', 'C')]
edge_colours = ['black' if not edge in red_edges else 'red'
                for edge in G.edges()]
black_edges = [edge for edge in G.edges() if edge not in red_edges] """

# Need to create a layout when doing
# separate calls to draw nodes and edges

conn = getconn()
cursor = conn.cursor()
cursor.execute("select rid,rname,rdesc,exitsdesc,xofct,yofct from roominfo where area='yz'")
rows = cursor.fetchall()
rid_rname_dict = {}
edge_list = []
init_pos = {}
fixed = []
for row in rows:
    rid = row[0]
    rname = row[1]
    rdesc = row[2]   
    exitsdesc = row[3]
    cursor.execute('select rid,nextrid,exit,bexit from roomrel where rid=?',(rid,))
    rels = cursor.fetchall()
    if len(rels)==0:
        continue
    rid_rname_dict[rid] = rname
    init_pos[rid] = (int(row[4])/5.0,int(row[5])/-5.0)
    for rel in rels:
        edge_list.append((rel[0],rel[1],rel[2],rel[3]))
conn.close()
for e in edge_list:
    if e[1] in rid_rname_dict.keys():
        G.add_edge(e[0],e[1])

LimitedG = nx.DiGraph()
LimitedG.add_edges_from(nx.bfs_edges(G,source='fafcccde039f147ba35240c82167154f', depth_limit=2))
LimitedG_node_name_dict = {}
for rid in LimitedG:
    LimitedG_node_name_dict[rid] = rid_rname_dict[rid]
dist = defaultdict(dict)
for rid1 in LimitedG:
    fixed.append(rid1)

        

plt.figure(figsize=(2.4,3))
plt.rcParams['savefig.dpi'] = 100 #图片像素
plt.rcParams['figure.dpi'] = 100 #分辨率

#pos =  nx.kamada_kawai_layout(G,pos=init_pos,center=(0,0))
#fixed = []
pos = nx.spring_layout(G,iterations=50,pos=init_pos)
#print pos
#print fixed
#labels = {"A":"阿里巴巴".decode("utf8"),"B":"腾讯".decode("utf8"),"C":"cat"}
nx.draw(LimitedG,pos, node_size=200,  edge_color="r", font_size=10, with_labels=True,labels=LimitedG_node_name_dict, font_family ='SimHei')
print plt.axis()
plt.show()

plt.savefig('plot1.png', dpi=100, transparent=True)

#%%
G = nx.DiGraph()
rid_rname_dict = {}
edge_list = []
init_pos = {}
fixed = []
conn = getconn()
cursor = conn.cursor()
cursor.execute('select t1.rid,nextrid,t2.rname,t2.xofct,t2.yofct,exit,bexit,cost from roomrel t1 left join roominfo t2 on t1.rid=t2.rid  ')
rows = cursor.fetchall()
conn.close()

for row in rows:
    rid = row[0]
    rid_rname_dict[rid] = row[2]
    init_pos[rid] = (int(row[3])/5.0,int(row[4])/-5.0)
    edge_list.append((row[0],row[1],row[5],row[6],row[7]))

for e in edge_list:
    if e[1] in rid_rname_dict.keys():
        G.add_edge(e[0],e[1],weight=e[4])



#pos =  nx.kamada_kawai_layout(G,pos=init_pos,center=(0,0))
#fixed = []
pos = nx.spring_layout(G,iterations=50,pos=init_pos)
#print pos
#print fixed
#%%
#labels = {"A":"阿里巴巴".decode("utf8"),"B":"腾讯".decode("utf8"),"C":"cat"}
LimitedG = nx.DiGraph()
LimitedG.add_edges_from(nx.bfs_edges(G,source='182aec296de2359255075564c4f8ed0a', depth_limit=2))
LimitedG_node_name_dict = {}
for rid in LimitedG:
    LimitedG_node_name_dict[rid] = rid_rname_dict[rid]
dist = defaultdict(dict)
for rid1 in LimitedG:
    fixed.append(rid1)

        

plt.figure(figsize=(5,5))
plt.rcParams['savefig.dpi'] = 100 #图片像素
plt.rcParams['figure.dpi'] = 100 #分辨率
nx.draw(LimitedG,pos, node_size=200,  edge_color="r", font_size=8, with_labels=True,labels=LimitedG_node_name_dict, font_family ='SimHei')
print plt.axis()
plt.show()

# %%
path = nx.shortest_path(G, source='fafcccde039f147ba35240c82167154f', target="37e39f2f1594c37fdf01f9a2fe548365",weight="weight")
for n in path:
    print rid_rname_dict[n]
cost = nx.shortest_path_length(G, source='fafcccde039f147ba35240c82167154f', target="37e39f2f1594c37fdf01f9a2fe548365",weight="weight")
print cost
# %%
