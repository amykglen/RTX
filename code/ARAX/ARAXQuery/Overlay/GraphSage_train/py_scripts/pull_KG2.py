import sys, os
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../")
from PullGraph import PullGraph

output_path = '~/work/RTX/code/reasoningtool/MLDrugRepurposing/Test_graphsage/data/'

## Connect to neo4j database
pullgraph = PullGraph(user='neo4j', password='precisionmedicine', url='bolt://kg2endpoint2.rtx.ai:7687')

## Pull a dataframe of all of the graph edges
#KG2_alledges=pullgraph.pull_graph()
#KG2_alledges.to_csv(output_path+'graph_edges.txt',sep='\t',index=None)

## Pulls a dataframe of all of the graph nodes with category label
#query = "match (n) with distinct n.id as id, n.name as name, n.category_label as category return id, name, category"
#res = pullgraph.neo4j_run_cypher_query(query)
#KG2_allnodes_label = pd.DataFrame(res.data())
#KG2_allnodes_label.to_csv(output_path+'graph_nodes_label.txt',sep='\t',index=None)

## Pulls a dataframe of all of the graph drug nodes
#drugs=pullgraph.pull_drugs()
#drugs.to_csv(output_path+'drugs.txt',sep='\t',index=None)

## Pulls a dataframe of all of the graph disease and phenotype nodes
diseases=pullgraph.pull_diseases()
diseases.to_csv(output_path+'diseases.txt',sep='\t',index=None)