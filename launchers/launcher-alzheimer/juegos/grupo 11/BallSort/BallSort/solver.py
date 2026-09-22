import copy
import time
from collections import Counter

def matrix_to_key(matrix):
    """Convierte la matriz de tubos en una tupla hashable para O(1) en visitados."""
    return tuple(tuple(col) for col in matrix)


class Node:
    def __init__(self, parent, matrix, arrCompleted, n, m, ntubes, lastMove, depth, evaluatedValue):
        self.parent = parent
        self.matrix = matrix
        self.arrCompleted = arrCompleted
        self.lastMove = lastMove
        self.depth = depth
        self.evaluatedValue = evaluatedValue
        self.n = n
        self.m = m
        self.ntubes = ntubes

    def getMatrix(self):
        return self.matrix
    
    def getArrCompleted(self):
        return self.arrCompleted
    
    def getLastMove(self):
        return self.lastMove
    
    def getDepth(self):
        return self.depth
    
    def getEvaluatedValue(self):
        return self.evaluatedValue
    
    def getParent(self):
        return self.parent
    
    def moveBall(self, fromCol, toCol):
        num = self.matrix[fromCol].pop(-1)
        self.matrix[toCol].append(num)
        if self.checkCompleted(self.matrix, toCol):
            self.arrCompleted[toCol] = 1
        else:
            self.arrCompleted[toCol] = 0
        if self.checkCompleted(self.matrix, fromCol):
            self.arrCompleted[fromCol] = 1
        else:
            self.arrCompleted[fromCol] = 0
        self.lastMove = (fromCol, toCol)

    def evaluateState(self):
        # Heurística 1: Penaliza bolas que no coinciden con la más común en cada tubo
        self.evaluatedValue = 0
        for column in self.matrix:
            if not column:
                continue
            numCount = Counter(column)
            if len(column) > 1:
                commonNumber = numCount.most_common(1)[0][0]
                for i in range(0, len(column)):
                    if column[i] != commonNumber:
                        self.evaluatedValue += (len(column) - i)
                        break
            elif len(column) == 1:
                self.evaluatedValue += 1

    def evaluateState2(self):
        # Heurística 2
        self.evaluatedValue = 0
        for column in self.matrix:
            if len(column) == 0:
                continue
            num = column[0]
            for i in range(0, len(column)):
                if column[i] == num:
                    self.evaluatedValue += 1
                else:
                    break

    def gameOver(self):
        return self.getArrCompleted().count(1) == self.n

    def checkCompleted(self, matrix, col):
        return len(set(matrix[col])) == 1 and len(matrix[col]) == self.m

    def validMove(self, fromCol, toCol):
        if len(self.matrix[fromCol]) > 0 and len(self.matrix[toCol]) < self.m and fromCol != toCol and not (
        self.arrCompleted[fromCol]):
            if len(self.matrix[toCol]) == 0:
                return True
            elif self.matrix[fromCol][-1] == self.matrix[toCol][-1]:
                return True
            else:
                return False
        else:
            return False

    def generateChilds(self, heuristic):
        childs = []
        last_from, last_to = self.getLastMove()
        for i in range(0, self.ntubes):
            if not self.matrix[i] or self.arrCompleted[i]:
                continue
            for j in range(0, self.ntubes):
                if i == j:
                    continue
                # Evitar deshacer inmediatamente el movimiento anterior
                if i == last_to and j == last_from:
                    continue
                if self.validMove(i, j):
                    newstate = Node(
                        self,
                        [list(col) for col in self.getMatrix()],
                        list(self.getArrCompleted()),
                        self.n,
                        self.m,
                        self.ntubes,
                        (i, j),
                        self.getDepth() + 1,
                        0
                    )
                    newstate.moveBall(i, j)
                    if heuristic == 1:
                        newstate.evaluateState()
                    elif heuristic == 2:
                        newstate.evaluateState2()
                    childs.append(newstate)
        return childs


class Graph:
    def __init__(self, root):
        self.root = root
        self.statesCounter = 1
        self.startTime = 0
        self.endTime = 0

    def breadthFirst(self, node):
        if node.gameOver():
            return node
        visited = {matrix_to_key(node.getMatrix())}
        states = [node]
        self.statesCounter = 1
        self.startTime = time.time()

        while states:
            # Límite de tiempo o estados para prevenir consumo infinito
            if len(visited) > 40000 or (time.time() - self.startTime) > 5.0:
                break
            state = states.pop(0)
            children = state.generateChilds(None)
            for child in children:
                key = matrix_to_key(child.getMatrix())
                if key not in visited:
                    if child.gameOver():
                        self.endTime = time.time()
                        return child
                    self.statesCounter += 1
                    visited.add(key)
                    states.append(child)
        return None

    def depthFirst(self, initState):
        if initState.gameOver():
            return initState
        visited = set()
        states = [initState]
        self.statesCounter = 1
        self.startTime = time.time()

        while states:
            if len(visited) > 40000 or (time.time() - self.startTime) > 5.0:
                break
            curr = states.pop()
            key = matrix_to_key(curr.getMatrix())
            if key in visited:
                continue
            visited.add(key)

            children = curr.generateChilds(None)
            for child in children:
                if child.gameOver():
                    self.endTime = time.time()
                    return child
                c_key = matrix_to_key(child.getMatrix())
                if c_key not in visited:
                    self.statesCounter += 1
                    states.append(child)
        return None

    def limitedDepthSearch(self, initState, limit):
        if initState.gameOver():
            return initState
        visited = set()
        states = [[initState, 0]]
        self.statesCounter = 1
        self.startTime = time.time()

        while states:
            if len(visited) > 40000 or (time.time() - self.startTime) > 5.0:
                break
            curr, depth = states.pop()
            if depth > limit:
                continue

            key = matrix_to_key(curr.getMatrix())
            if key in visited:
                continue
            visited.add(key)

            children = curr.generateChilds(None)
            for child in children:
                if child.gameOver():
                    self.endTime = time.time()
                    return child
                c_key = matrix_to_key(child.getMatrix())
                if c_key not in visited:
                    self.statesCounter += 1
                    states.append([child, depth + 1])
        return None

    def progressiveDeepening(self, initState, progress):
        limit = progress
        while limit <= 40:
            res = self.limitedDepthSearch(initState, limit)
            if res:
                return res
            limit += progress
        return None

    def uniformCostSearch(self, initState):
        if initState.gameOver():
            return initState
        visited = {matrix_to_key(initState.getMatrix())}
        states = [[initState, 0]]
        self.statesCounter = 1
        self.startTime = time.time()

        while states:
            if len(visited) > 40000 or (time.time() - self.startTime) > 5.0:
                break
            states.sort(key=lambda x: x[1])
            state = states.pop(0)[0]
            children = state.generateChilds(None)
            for child in children:
                key = matrix_to_key(child.getMatrix())
                if key not in visited:
                    if child.gameOver():
                        self.endTime = time.time()
                        return child
                    self.statesCounter += 1
                    visited.add(key)
                    states.append([child, child.getDepth()])
        return None

    def greedySearch(self, initState, heuristic):
        if initState.gameOver():
            return initState
        visited = {matrix_to_key(initState.getMatrix())}
        states = [[initState, initState.getEvaluatedValue()]]
        self.statesCounter = 1
        self.startTime = time.time()

        while states:
            if len(visited) > 40000 or (time.time() - self.startTime) > 5.0:
                break
            states.sort(key=lambda x: x[1])
            if heuristic == 2:
                states.reverse()

            state = states.pop(0)[0]
            children = state.generateChilds(heuristic)

            for child in children:
                key = matrix_to_key(child.getMatrix())
                if key not in visited:
                    if child.gameOver():
                        self.endTime = time.time()
                        return child
                    self.statesCounter += 1
                    visited.add(key)
                    states.append([child, child.getEvaluatedValue()])
        return None

    def aStarSearch(self, initState, heuristic=1):
        if initState.gameOver():
            return initState
        visited = {matrix_to_key(initState.getMatrix())}
        states = [[initState, initState.getEvaluatedValue() + initState.getDepth()]]
        self.statesCounter = 1
        self.startTime = time.time()

        while states:
            if len(visited) > 40000 or (time.time() - self.startTime) > 5.0:
                break
            states.sort(key=lambda x: x[1])
            state = states.pop(0)[0]

            children = state.generateChilds(heuristic)
            for child in children:
                key = matrix_to_key(child.getMatrix())
                if key not in visited:
                    if child.gameOver():
                        self.endTime = time.time()
                        return child
                    self.statesCounter += 1
                    visited.add(key)
                    states.append([child, (child.getEvaluatedValue() * 3) + child.getDepth()])
        return None

    def solve(self, rootnode, solver):
        if solver == 1:
            return self.aStarSearch(rootnode, 1)
        elif solver == 2:
            return self.greedySearch(rootnode, 1)
        elif solver == 3:
            return self.depthFirst(rootnode)
        elif solver == 4:
            return self.breadthFirst(rootnode)
        elif solver == 5:
            return self.uniformCostSearch(rootnode)
        elif solver == 6:
            return self.progressiveDeepening(rootnode, 5)
        elif solver == 7:
            return self.limitedDepthSearch(rootnode, 30)
        else:
            return self.aStarSearch(rootnode, 1)

    def getHint(self, rootnode, solver):
        if rootnode.gameOver():
            return None
        node = self.solve(rootnode, solver)
        if not node:
            return -1
        moves = []
        currNode = node
        while currNode.getParent() is not None:
            moves.append(currNode.getLastMove())
            currNode = currNode.getParent()
        if not moves:
            return None
        return moves[-1]  # Primer movimiento desde el estado actual

    def getAutoSolve(self, rootnode, solver):
        if rootnode.gameOver():
            return []
        node = self.solve(rootnode, solver)
        if not node:
            return []
        moves = []
        currNode = node
        while currNode.getParent() is not None:
            moves.append(currNode.getLastMove())
            currNode = currNode.getParent()
        moves.reverse()
        return moves
