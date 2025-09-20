from scipy import sparse
import networkx as nx
import random as rd
from scipy.optimize import linear_sum_assignment

def findCentroid(locations):
    # Find the centroid of the locations
    centerX = 0
    centerY = 0
    for loc in locations:
        centerX += loc[0]
        centerY += loc[1]
    
    centroid = (centerX/len(locations), centerY/len(locations))
    return centroid

def matchDisconnected(availableNodes, availableLocations, nodesToLoc):
    # Match nodes that have a degree of zero
    rd.shuffle(availableNodes)
    rd.shuffle(availableLocations)
    for i, n in enumerate(availableNodes):
        nodesToLoc[n] = availableLocations[i]
    return nodesToLoc

def nodeLocMatching(matrix, knownLocations, locations, locationStats, pop, disconnected):
    avgDist, centroid = locationStats
    nodesToLoc = {}

    # Create a NetworkX graph of the social network
    cx = sparse.coo_matrix(matrix)
    springGraph = nx.Graph()
    for i, j, v in zip(cx.row, cx.col, cx.data):
        springGraph.add_edge(i, j, weight=pop)
    
     # Add known locations as fixed nodes to the graph
    fixedNodes = set()
    fixedLocs = set()
    for n in knownLocations:
        fixedNodes.add(n)
        fixedLocs = knownLocations[n]
        nodesToLoc[n] = knownLocations[n]

    # Run the spring layout algorithm
    if fixedNodes:
        nodePositions = nx.spring_layout(springGraph, pos=knownLocations, fixed=fixedNodes, k = avgDist)
    else:
        nodePositions = nx.spring_layout(springGraph, center=centroid, k = avgDist)

    unmatchedLocs = [i for i in locations if i not in fixedLocs]
    unmatchedNodes = [i for i in range(pop) if i not in fixedNodes and i not in disconnected]
    
    nodesToLoc = matchNewLocationsOptimal(nodesToLoc, [i for i in unmatchedNodes], [i for i in unmatchedLocs], nodePositions)
    nodesToLoc = matchDisconnected([i for i in disconnected if i not in nodesToLoc], unmatchedLocs, nodesToLoc)

    return nodesToLoc

def matchNewLocationsOptimal(nodesToLoc, unmatchedNodes, unmatchedLocs, nodePositions):
    # Match nodes to the closest available location using modified Jonker-Volgenant algorithm
    costMatrix = []
    for node in unmatchedNodes:
        nodeLoc = nodePositions[node]
        costMatrix.append([((float(coord[0] - nodeLoc[0]))**2 + ((float(coord[1] - nodeLoc[1])**2)))**0.5 for coord in unmatchedLocs])
    row_ind, col_ind = linear_sum_assignment(costMatrix)

    for idx in range(len(row_ind)):
        nodesToLoc[unmatchedNodes[row_ind[idx]]] = unmatchedLocs[col_ind[idx]]
    return nodesToLoc

def graphDrawingGreedy(matrix, locations, knownLocations):
    # Input:
    #   matrix: adjacency matrix with all nodes in the network
    #   locations: list of the coordinates of the possible locations
    #   knownLocations: dictionary which maps nodes to known locations
    # Output:
    #   Dictionary which maps nodes to the given locations

    nodeConnections = {}
    disconnected = []
    for n, row in enumerate(matrix):
        nodeConnections[n] = {i for i, j in enumerate(row) if j}
        if not nodeConnections[n]:
            disconnected.append(n)

    lenDists = 0
    avgDist = 0
    for loc in locations:
        for nLoc in locations:
            if loc != nLoc:
                dist = ((nLoc[0] - loc[0])**2 + ((nLoc[1] - loc[1])**2))**0.5
                lenDists += 1
                avgDist+= dist
    avgDist = avgDist/lenDists
    
    centroid = findCentroid(locations)
    locationStats = (avgDist, centroid)
    
    nodesToLoc = nodeLocMatching(matrix, knownLocations, locations,  locationStats, len(locations), disconnected)
    return nodesToLoc