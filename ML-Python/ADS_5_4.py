
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.2** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-social-network-analysis/resources/yPcBs) course resource._
# 
# ---

# # Assignment 4

# In[1]:

import networkx as nx
import pandas as pd
import numpy as np
import pickle


# ---
# 
# ## Part 1 - Random Graph Identification
# 
# For the first part of this assignment you will analyze randomly generated graphs and determine which algorithm created them.

# In[2]:

P1_Graphs = pickle.load(open('A4_graphs','rb'))
P1_Graphs


# <br>
# `P1_Graphs` is a list containing 5 networkx graphs. Each of these graphs were generated by one of three possible algorithms:
# * Preferential Attachment (`'PA'`)
# * Small World with low probability of rewiring (`'SW_L'`)
# * Small World with high probability of rewiring (`'SW_H'`)
# 
# Anaylze each of the 5 graphs and determine which of the three algorithms generated the graph.
# 
# *The `graph_identification` function should return a list of length 5 where each element in the list is either `'PA'`, `'SW_L'`, or `'SW_H'`.*

# In[3]:

def deg_hist(G):
    degrees = G.degree()
    degree_values = sorted(set(degrees.values()))
    histogram = [list(degrees.values()).count(i)/float(nx.number_of_nodes( G)) for i in degree_values]
    return histogram

def graph_identification():
   
    # Your Code Here
    graphid = []
    
    for G in P1_Graphs:
        if (len(deg_hist(G)) > 20):
            graphid.append('PA')
        elif (nx.average_clustering(G) < 0.2):
            graphid.append('SW_H')
        else:
            graphid.append('SW_L')

#    for G in P1_Graphs:
#        print(deg_hist(G), nx.average_clustering(G), nx.average_shortest_path_length(G))
        
    return graphid # Your Answer Here

graph_identification()


# ---
# 
# ## Part 2 - Company Emails
# 
# For the second part of this assignment you will be workking with a company's email network where each node corresponds to a person at the company, and each edge indicates that at least one email has been sent between two people.
# 
# The network also contains the node attributes `Department` and `ManagementSalary`.
# 
# `Department` indicates the department in the company which the person belongs to, and `ManagementSalary` indicates whether that person is receiving a management position salary.

# In[4]:

G = nx.read_gpickle('email_prediction.txt')

print(nx.info(G))


# ### Part 2A - Salary Prediction
# 
# Using network `G`, identify the people in the network with missing values for the node attribute `ManagementSalary` and predict whether or not these individuals are receiving a management position salary.
# 
# To accomplish this, you will need to create a matrix of node features using networkx, train a sklearn classifier on nodes that have `ManagementSalary` data, and predict a probability of the node receiving a management salary for nodes where `ManagementSalary` is missing.
# 
# 
# 
# Your predictions will need to be given as the probability that the corresponding employee is receiving a management position salary.
# 
# The evaluation metric for this assignment is the Area Under the ROC Curve (AUC).
# 
# Your grade will be based on the AUC score computed for your classifier. A model which with an AUC of 0.88 or higher will receive full points, and with an AUC of 0.82 or higher will pass (get 80% of the full points).
# 
# Using your trained classifier, return a series of length 252 with the data being the probability of receiving management salary, and the index being the node id.
# 
#     Example:
#     
#         1       1.0
#         2       0.0
#         5       0.8
#         8       1.0
#             ...
#         996     0.7
#         1000    0.5
#         1001    0.0
#         Length: 252, dtype: float64

# In[5]:


from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import MinMaxScaler

def mgmt(node):
    if (node[1]['ManagementSalary'] == 0.):
        return 0
    elif (node[1]['ManagementSalary'] == 1.):
        return 1
    else:
        return None

def salary_predictions():
    
    # Your Code Here
    df = pd.DataFrame(index=G.nodes())
    df['clustering'] = pd.Series(nx.clustering(G))
#    df['eccentricity'] = pd.Series(nx.eccentricity(G))
    df['degree'] = pd.Series(G.degree())
    df['degree_centrality'] = pd.Series(nx.degree_centrality(G))
    df['closeness_centrality'] = pd.Series(nx.closeness_centrality(G, normalized=True))
    df['betweenness_centrality'] = pd.Series(nx.betweenness_centrality(G, normalized=True, endpoints=False))
    df['betweenness_centrality_ep'] = pd.Series(nx.betweenness_centrality(G, normalized=True, endpoints=True))
    df['page_rank'] = pd.Series(nx.pagerank(G))
    df['management'] = pd.Series([mgmt(node) for node in G.nodes(data=True)])

    df_src = df[~pd.isnull(df['management'])]
    df_src['management'] = df_src['management'].astype(int)
    df_pred = df[pd.isnull(df['management'])]
    
    features = ['clustering', 'degree', 'degree_centrality', 'closeness_centrality', 'betweenness_centrality', 'betweenness_centrality_ep', 'page_rank']
    
#    X = df_src[features]
#    y = df_src['management']
#    
#    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)
    
    X_train = df_src[features]
    y_train = df_src['management']
    X_test = df_pred[features]
    
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
#    clf = SVC(kernel='rbf')
#    grid_values = {'gamma': [0.001, 0.01, 0.05, 0.1, 1, 10, 100]}

# alternative metric to optimize over grid parameters: AUC
#    grid_clf_auc = GridSearchCV(clf, param_grid = grid_values, scoring = 'roc_auc')
#    grid_clf_auc.fit(X_train_scaled, y_train)
#    y_decision_fn_scores_auc = grid_clf_auc.decision_function(X_test_scaled) 

    clf = SVC(gamma=10, probability=True)
    clf.fit(X_train_scaled, y_train)
    prob = clf.predict_proba(X_test_scaled)[:, 1]
    
#    print('Test set AUC: ', roc_auc_score(y_test, prob))
    return pd.Series(prob, X_test.index) # Your Answer Here
                                 
salary_predictions()


# ### Part 2B - New Connections Prediction
# 
# For the last part of this assignment, you will predict future connections between employees of the network. The future connections information has been loaded into the variable `future_connections`. The index is a tuple indicating a pair of nodes that currently do not have a connection, and the `Future Connection` column indicates if an edge between those two nodes will exist in the future, where a value of 1.0 indicates a future connection.

# In[6]:

future_connections = pd.read_csv('Future_Connections.csv', index_col=0, converters={0: eval})
future_connections.head(10)


# Using network `G` and `future_connections`, identify the edges in `future_connections` with missing values and predict whether or not these edges will have a future connection.
# 
# To accomplish this, you will need to create a matrix of features for the edges found in `future_connections` using networkx, train a sklearn classifier on those edges in `future_connections` that have `Future Connection` data, and predict a probability of the edge being a future connection for those edges in `future_connections` where `Future Connection` is missing.
# 
# 
# 
# Your predictions will need to be given as the probability of the corresponding edge being a future connection.
# 
# The evaluation metric for this assignment is the Area Under the ROC Curve (AUC).
# 
# Your grade will be based on the AUC score computed for your classifier. A model which with an AUC of 0.88 or higher will receive full points, and with an AUC of 0.82 or higher will pass (get 80% of the full points).
# 
# Using your trained classifier, return a series of length 122112 with the data being the probability of the edge being a future connection, and the index being the edge as represented by a tuple of nodes.
# 
#     Example:
#     
#         (107, 348)    0.35
#         (542, 751)    0.40
#         (20, 426)     0.55
#         (50, 989)     0.35
#                   ...
#         (939, 940)    0.15
#         (555, 905)    0.35
#         (75, 101)     0.65
#         Length: 122112, dtype: float64

# In[11]:

import time
from sklearn.svm import SVC
# from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import MinMaxScaler

#def printt(X):
#    print(X, time.clock())

def new_connections_predictions():
    
    # Your Code Here
#    printt("start")
    
    for node in G.nodes():
        G.node[node]['community'] = G.node[node]['Department']
        
#    printt(nx.info(G))
        
    jc = list(nx.jaccard_coefficient(G))
#    printt("jc")
    rai = list(nx.resource_allocation_index(G))
#    printt("rai")
    aai = list(nx.adamic_adar_index(G))
#    printt("aai")
    pa = list(nx.preferential_attachment(G))
#    printt("pa")
    cnsh = list(nx.cn_soundarajan_hopcroft(G))
#    printt("cnsh")
    raish = list(nx.ra_index_soundarajan_hopcroft(G))
#    printt("raish")
    wic = list(nx.within_inter_cluster(G))
#    printt("wic")
    
    df = pd.DataFrame(index=[(edge[0], edge[1]) for edge in jc])
#    printt("df created")
    df['jc'] = [edge[2] for edge in jc]
#    printt("df[jc]")
    
    newdf = pd.DataFrame(index=[(edge[0], edge[1]) for edge in rai])
    newdf['rai'] = [edge[2] for edge in rai]
#    printt("newdf a")
    df = df.join(newdf, how='outer')
    df['rai']=df['rai'].fillna(value=0)
#    printt("join a")
    
    newdf = pd.DataFrame(index=[(edge[0], edge[1]) for edge in aai])
    newdf['aai'] = [edge[2] for edge in aai]
    df = df.join(newdf, how='outer')
    df['aai']=df['aai'].fillna(value=0)
    
    newdf = pd.DataFrame(index=[(edge[0], edge[1]) for edge in pa])
    newdf['pa'] = [edge[2] for edge in pa]
    df = df.join(newdf, how='outer')
    df['pa']=df['pa'].fillna(value=0)
    
    newdf = pd.DataFrame(index=[(edge[0], edge[1]) for edge in cnsh])
    newdf['cnsh'] = [edge[2] for edge in cnsh]
    df = df.join(newdf, how='outer')
    df['cnsh']=df['cnsh'].fillna(value=0)
    
    newdf = pd.DataFrame(index=[(edge[0], edge[1]) for edge in raish])
    newdf['raish'] = [edge[2] for edge in raish]
    df = df.join(newdf, how='outer')
    df['raish']=df['raish'].fillna(value=0)
    
    newdf = pd.DataFrame(index=[(edge[0], edge[1]) for edge in wic])
    newdf['wic'] = [edge[2] for edge in wic]
    df = df.join(newdf, how='outer')
    df['wic']=df['wic'].fillna(value=0)
    
#    printt("about to join fc")
    
    df = df.join(future_connections, how='outer')
    
#    print("dataframe shape", df.shape)
    
    df_src = df[~pd.isnull(df['Future Connection'])]
    df_src['Future Connection'] = df_src['Future Connection'].astype(int)
    df_pred = df[pd.isnull(df['Future Connection'])]
    
    features = ['jc', 'rai', 'aai', 'pa', 'cnsh', 'raish', 'wic']
    
#    printt(features)
    
    X = df_src[features]
    y = df_src['Future Connection']
    
#    printt(X.head(10))
#    printt(y.head(10))
    
    X_train, _, y_train, _ = train_test_split(X, y, test_size = 0.05, train_size = 0.05, random_state=0)
#    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.05, train_size = 0.05, random_state=0)
    
#    X_train = df_src[features]
#    y_train = df_src['Future Connection']

    X_test = df_pred[features]
    
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
#    printt(X_train_scaled)
#    printt(X_test_scaled)
#    printt(y_train)
#    printt(y_test)
    
#    printt("X train test split and scaled")

#    print("X_train shape", X_train.shape)
#    print("X_test shape", X_test.shape)
#    print("y_train shape", y_train.shape)
#    print("y_test shape", y_test.shape)
    
    clf = SVC(kernel='rbf', probability=True)
#    printt(clf)
#    grid_values = {'gamma': [0.001, 0.01, 0.05, 0.1, 1, 10, 100]}

# alternative metric to optimize over grid parameters: AUC
#    grid_clf_auc = GridSearchCV(clf, param_grid = grid_values, scoring = 'roc_auc')
#    printt("done grid search")
#    grid_clf_auc.fit(X_train_scaled, y_train)
#    printt("done fit")
#    y_decision_fn_scores_auc = grid_clf_auc.decision_function(X_test_scaled) 
#    printt("done decision function")

#    clf = SVC(gamma=10, probability=True)
#    print("before fit")
    clf.fit(X_train_scaled, y_train)
#    print("done fit")

    prob = clf.predict_proba(X_test_scaled)[:, 1]
    pred = pd.Series(prob, X_test.index)
    
    final = future_connections[pd.isnull(future_connections['Future Connection'])]
    final['prob'] = [pred[edge] for edge in final.index]
#    print("shape final", final.shape)
    
#    print('Test set AUC: ', roc_auc_score(y_test, prob))
#    printt('Grid best parameter (max. AUC): ', grid_clf_auc.best_params_)
#    printt('Grid best score (AUC): ', grid_clf_auc.best_score_)
#    return pd.Series(y_decision_fn_scores_auc, X_test.index) # Your Answer Here
    return final['prob']

new_connections_predictions()


# In[7]:




# In[6]:




# In[ ]:



