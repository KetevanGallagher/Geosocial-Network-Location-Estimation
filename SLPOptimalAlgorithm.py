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

def SLPOptimal(matrix, locations, knownLocations):
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
        
        SLPOptimalNodesToLoc = {}
        for i in knownLocations:
            SLPOptimalNodesToLoc[i] = knownLocations[i]
        SLPNodes = [i for i in range(pop) if i not in knownLocations and i not in disconnected]
        SLPLocs = [loc for loc in locations if loc not in knownLocSet]
        
        SLPOptimalNodesToLoc = matchNewLocationsOptimal(SLPOptimalNodesToLoc, SLPNodes, SLPLocs, SLPNodePositions)
        SLPOptimalNodesToLoc = matchDisconnected(disconnected, SLPLocs, SLPOptimalNodesToLoc)   

    else:
        print("This algorithm requires at least one known location")
    
    return SLPOptimalNodesToLoc