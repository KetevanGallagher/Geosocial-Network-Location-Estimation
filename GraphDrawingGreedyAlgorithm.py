from scipy import sparse
import networkx as nx
import random as rd

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

def nodeLocMatching(matrix, knownLocations, locations, nodeConnections, locationStats, pop, disconnected):
    avgDist, maxDist, centroid = locationStats
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
    
    nodesToLoc = matchNewLocationsGreedy(nodesToLoc, [i for i in unmatchedNodes], [i for i in unmatchedLocs], nodePositions, nodeConnections, maxDist)
    nodesToLoc = matchDisconnected([i for i in disconnected if i not in nodesToLoc], unmatchedLocs, nodesToLoc)

    return nodesToLoc

def matchNewLocationsGreedy(nodesToLoc, unmatchedNodes, unmatchedLocs, nodePositions, nodeConnections, maxDist):
    # Match nodes to the closest available location, starting with the nodes with the highest degree
    while unmatchedNodes:
        currentNode = 0
        maxLen = 0
        for node in nodesToLoc:
            if len(nodeConnections[node]) > maxLen and len([i for i in nodeConnections[node] if i not in nodesToLoc]) != 0:
                maxLen = len(nodeConnections[node])
                currentNode = node
        currentNNode = 0
        maxNLen = 0
        for node in nodeConnections[currentNode]:
            if node not in nodesToLoc:
                if len(nodeConnections[node]) > maxNLen:
                    maxNLen = len(nodeConnections[node])
                    currentNNode = node
        cNodePos = nodePositions[currentNNode]

        
        minDist =  maxDist**2
        minLoc = unmatchedLocs[0]
        for loc in unmatchedLocs:
            dist = ((float(loc[0] - cNodePos[0]))**2 + ((float(loc[1] - cNodePos[1])**2)))**0.5
            if dist < minDist:
                minLoc = loc
                minDist = dist
        nodesToLoc[currentNNode] = minLoc
        unmatchedLocs.remove(minLoc)
        unmatchedNodes.remove(currentNNode)
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

    maxDist = 0
    lenDists = 0
    avgDist = 0
    for loc in locations:
        for nLoc in locations:
            if loc != nLoc:
                dist = ((nLoc[0] - loc[0])**2 + ((nLoc[1] - loc[1])**2))**0.5
                if dist > maxDist:
                    maxDist = dist
                lenDists += 1
                avgDist+= dist
    avgDist = avgDist/lenDists
    
    centroid = findCentroid(locations)
    locationStats = (avgDist, maxDist, centroid)
    
    nodesToLoc = nodeLocMatching(matrix, knownLocations, locations, nodeConnections,  locationStats, len(locations), disconnected)
    return nodesToLoc