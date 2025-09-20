import random as rd
from scipy.optimize import linear_sum_assignment

def matchDisconnected(availableNodes, availableLocations, nodesToLoc):
    # Match nodes that have a degree of zero
    rd.shuffle(availableNodes)
    rd.shuffle(availableLocations)
    for i, n in enumerate(availableNodes):
        nodesToLoc[n] = availableLocations[i]
    return nodesToLoc

def iterateSLP(unmatched, nodeConnections, SLPNodePositions):
    newMatchedNodes = {}
    for node in nodeConnections:
        if node in SLPNodePositions:
            continue
        kNeighbors = []
        for neighbor in nodeConnections[node]:
            if neighbor in SLPNodePositions:
                kNeighbors.append(neighbor)
        if kNeighbors:
            unmatched.remove(node)
            kNeighborX = sum([SLPNodePositions[n][0] for n in kNeighbors])/len(kNeighbors)
            kNeighborY = sum([SLPNodePositions[n][1] for n in kNeighbors])/len(kNeighbors)
            newMatchedNodes[node] = (kNeighborX, kNeighborY)
    return unmatched, newMatchedNodes

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

def SLPGreedy(matrix, locations, knownLocations):
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

    pop = len(locations)
    knownLocSet = {v for i, v in knownLocations.items()}
    
    if knownLocations != 0:
        SLPNodePositions = {}
        for i in knownLocations:
            SLPNodePositions[i] = knownLocations[i]
        
        unmatchedSLPNodes = [i for i in range(pop) if i not in knownLocations and i not in disconnected]
        while unmatchedSLPNodes:
            unmatchedSLPNodes, updatedMatched = iterateSLP(unmatchedSLPNodes, nodeConnections, SLPNodePositions)
            for n in updatedMatched:
                SLPNodePositions[n] = updatedMatched[n]
        
        SLPGreedyNodesToLoc = {}
        for i in knownLocations:
            SLPGreedyNodesToLoc[i] = knownLocations[i]
        SLPNodes = [i for i in range(pop) if i not in knownLocations and i not in disconnected]
        SLPLocs = [loc for loc in locations if loc not in knownLocSet]
        
        SLPGreedyNodesToLoc = matchNewLocationsGreedy(SLPGreedyNodesToLoc, SLPNodes, SLPLocs, SLPNodePositions, nodeConnections, maxDist)
        SLPGreedyNodesToLoc = matchDisconnected(disconnected, SLPLocs, SLPGreedyNodesToLoc)


    else:
        print("This algorithm requires at least one known location")
    
    return SLPGreedyNodesToLoc