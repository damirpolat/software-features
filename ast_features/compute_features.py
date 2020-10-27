import networkx as nx
import statistics as stats
from collections import Counter
from scipy.stats import entropy
import os
import sys
import random


def parseASTdump(filenames):
    nodes={}
    node_types={}
    operators={}
    edges=[]
    context=[]
    for f in filenames:
        #print(f)
        with open(f) as astdump:
            nline=0
    
            for l in astdump:
        
                try:
                    words=l.strip().split(" 0x")
                    nid="0x"+words[1].split(" ")[0]
                    depth=int((1+words[0].find("-"))/2)
                    if depth>0:
                        nodes[nid]=words[0].split("-")[-1]
                        if len(words[1].split("> '"))>1:
                            node_types[nid]=words[1].split("> '")[1].split("' ")[0].strip("'")
                        if is_operator(nodes[nid]):
                            operators[nid]=words[1].split(" ")[-1]
                        #print([context[depth-1],nid])
                        edges.append([context[depth-1],nid])
                        if len(context)<depth+1:
                            context.append(nid)
                        else:
                            context[depth]=nid
                    else:
                        if len(nodes.keys())==0:
                            context.append(nid)
                            nodes[nid]=words[0].split("-")[-1]
                    
                except:
                    #print(l)
                    continue
    return nodes, edges, node_types, operators

def is_stmt(n):
    return n.endswith("Stmt") or n.endswith("Directive") or n.endswith("Case") or n.endswith("Expr") or n.endswith("Field") 
def is_type(n):
    return n.endswith("Type") or n.startswith("Type") or n.startswith("TypeParm")
def is_decl(n):
    return n.endswith("Decl") or n.endswith("Record") or n=="ClassTemplateSpecialization"
def is_attr(n):
    return n.endswith("Attr")
def is_operator(n):
    return n.endswith("Operator")
def is_literal(n):
    return n.endswith("Literal")

def compute_features(net,nodes,node_types,operators):
    features=[]
    #node degree
    degrees= [d for (n,d) in net.degree]
    #print(degrees)
    count = Counter(degrees)
    features = features + [min(degrees),max(degrees),stats.mean(degrees),stats.variance(degrees),entropy([count[i] for i in range(max(degrees))])]
    #transitivity
    features.append(nx.transitivity(net))
    #clustering
    clustering=[nx.clustering(net,n) for n in net.nodes]
    #print(clustering)
    count = Counter(clustering)
    features = features + [min(clustering),max(clustering),stats.mean(clustering),stats.variance(clustering)]
    #shortest path
    for i in nodes.keys():
        if nodes[i]=="TranslationUnitDecl":
            root=i
            break;
    leaflist=[node for node, outdegree in net.out_degree(net.nodes()) if outdegree == 0]
    lengths=[nx.shortest_path_length(net,source=root,target=n) for n in leaflist]
    #print(lengths)
    count = Counter(lengths)
    features = features + [min(lengths),max(lengths),stats.mean(lengths),stats.variance(lengths),entropy([count[i] for i in range(max(lengths))])] 
    #check node type
    nbStmt=0
    nbType=0
    nbDecl=0
    nbAttr=0
    nbOperator=0
    nbLiteral=0
    for i in nodes.keys():
        if is_stmt(nodes[i]):
            nbStmt+=1
        elif is_type(nodes[i]):
            nbType+=1
        elif is_decl(nodes[i]):
            nbDecl+=1
        elif is_attr(nodes[i]):
            nbAttr+=1
        elif is_operator(nodes[i]):
            nbOperator+=1
        elif is_literal(nodes[i]):
            nbLiteral+=1
        else :
            if nodes[i].endswith("Record") :
                print(nodes[i])
    total=nbStmt+nbType+nbDecl+nbAttr+nbOperator+nbLiteral
    features = features+[nbStmt/total,nbType/total,nbDecl/total,nbAttr/total,nbOperator/total,nbLiteral/total]
    
    #check successor types
    # in order: short, int, long, long long, float, double
    operationOn=[0,0,0,0,0,0]
    nbOperations=0
    bitwise=0
    typeTransitions=[0,0,0,0,0,0,
                     0,0,0,0,0,0,
                     0,0,0,0,0,0,
                     0,0,0,0,0,0,
                     0,0,0,0,0,0,
                     0,0,0,0,0,0]
    for i in range(min(10000,len(edges))):
        e=random.choice(edges)
        if is_stmt(nodes[e[0]]):
            i=0
        elif is_type(nodes[e[0]]):
            i=1
        elif is_decl(nodes[e[0]]):
            i=2
        elif is_attr(nodes[e[0]]):
            i=3
        elif is_operator(nodes[e[0]]):
            i=4
            nbOperations+=1
            if e[1] in node_types.keys():
                nbB=sum(operationOn)
                if node_types[e[1]].endswith('short'):
                    operationOn[0]+=1
                if node_types[e[1]].endswith('int'):
                    operationOn[1]+=1
                if node_types[e[1]].endswith('long long'):
                    operationOn[3]+=1
                elif node_types[e[1]].endswith('long'):
                    operationOn[2]+=1
                if node_types[e[1]].endswith('float'):
                    operationOn[4]+=1
                if node_types[e[1]].endswith('double'):
                    operationOn[5]+=1
                if operators[e[0]] in ["'&'","'|'","'>>'","'<<'","'^'","'~'"] and sum(operationOn)!=nbB:
                    bitwise+=1
        elif is_literal(nodes[e[0]]):
            i=5
        else:
            continue
        if is_stmt(nodes[e[1]]):
            j=0
        elif is_type(nodes[e[1]]):
            j=1
        elif is_decl(nodes[e[1]]):
            j=2
        elif is_attr(nodes[e[1]]):
            j=3
        elif is_operator(nodes[e[1]]):
            j=4
        elif is_literal(nodes[e[1]]):
            j=5
        else:
            continue
        typeTransitions[i+6*j]+=1
    
    features=features+typeTransitions+[f"{(opOn/nbOperations):.5f}" if nbOperations>0 else 0 for opOn in operationOn]+[f"{(bitwise/nbOperations):.5f}" if nbOperations>0 else 0]
    return features

if __name__ =='__main__':
    print("solver,"
          +"nb_nodes,nb_edges,"
          +"degree_min,degree_max,degree_mean,degree_variance,degree_entropy,"
          +"transitivity,"
          +"clustering_min,clustering_max,clustering_mean,clustering_variance,"
          +"path_min,paths_max,path_mean,path_variance, path_entropy,"
          +"Stmt,Type,Decl,Attribute,Operator,Literal,"
          +"edge_ss,edge_st,edge_sd,edge_sa,edge_so,edge_sl,"
          +"edge_ts,edge_tt,edge_td,edge_ta,edge_to,edge_tl,"
          +"edge_ds,edge_dt,edge_dd,edge_da,edge_do,edge_dl,"
          +"edge_as,edge_at,edge_ad,edge_aa,edge_ao,edge_al,"
          +"edge_os,edge_ot,edge_od,edge_oa,edge_oo,edge_ol,"
          +"edge_ls,edge_lt,edge_ld,edge_la,edge_lo,edge_ll,"
          +"op_short,op_int,op_long,op_long_long,op_float,op_double,op_bit"
          +"\n")
    
    nodes, edges, node_types, operators = parseASTdump(sys.argv[1:])
    #print(edges)
    #print(nodes)
    G = nx.DiGraph()
    G.add_edges_from(edges)
    name="/".join(sys.argv[1].split("/")[1:-1])
    
    features=[len(G.nodes),len(G.edges)]
    features=features+compute_features(G,nodes,node_types,operators)
    
        
    print(name+","+",".join([str(f) for f in features])+"\n")
