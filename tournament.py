#!/usr/bin/env python
#*******************************************************************************
# utttsim.py
#
# Program to simulate a game of Ultimate Tic-Tac-Toe between two players of
# certain characteristics
# 
# Created by James Cheng
#*******************************************************************************
import sys, getopt, time, datetime
import glob, operator
import random
from itertools import combinations

# Board set-up
# | y\x | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
# -------------------------------------------
# |  0  |           |           |           |
# |  1  |     0     |     3     |     6     |
# |  2  |           |           |           |
# -------------------------------------------
# |  3  |           |           |           |
# |  4  |     1     |     4     |     7     |
# |  5  |           |           |           |
# -------------------------------------------
# |  6  |           |           |           |
# |  7  |     2     |     5     |     8     |
# |  8  |           |           |           |
# -------------------------------------------

class Board:
    def __init__(self):
        self.grid = [[-1 for x in xrange(9)] for x in xrange(9)]
        self.decided = [-1 for x in xrange(9)]
        # This is a hack, could replace with better method to find winning combos
        self.wincombos = [(0, 1, 2), (0, 3, 6), (0, 4, 8), (1, 4, 7),
                         (2, 4, 6), (2, 5, 8), (3, 4, 5), (6, 7, 8)]
        self.nextBoard = -1 #in range 0-8, -1 for player's choice

    def printBoard(self):
        for row in self.grid:
            print row


# A gene is a list of values showing a player's preferences on different
# attributes on the board
# indices 0-2: values for center, edge, corner for an individual piece
# indices 3-7: values for position relative to own pieces
# indices 8-12: values for position relative to the opponent's pieces
# *for now assume solutions that lead to a decided board are not favored

class Players:
    def __init__(self, pop, id1, id2):
        self.ids = [id1, id2]
        self.genes = [pop[id1].chromosome, pop[id2].chromosome]
        self.winBoard = [[[] for x in xrange(2)] for x in xrange(9)]
        self.offset = 4
        self.oppoffset = 6
        #self.sitweight = 3 or sitweight

#class Population: #to be integrated with Environment
#	def __init__(self, popsize):
#		self.population = [[random.randint(-1, 1) for x in xrange(13)] for x in xrange(popsize)]
#		self.offset = 3
#		self.oppoffset = 5
#
#
#	def printPop(self):
#		for phenotype in self.population:
#			print phenotype

#class Records: #to be integrated with Environment?
#	def __init__(self, popsize):
#		self.popsize = popsize
#		self.wins = [0 for x in xrange(popsize)]
#		self.losses = [0 for x in xrange(popsize)]
#		self.ties = [0 for x in xrange(popsize)]



# Function definitions

#def printRec(Rec, Pop):
#	print "Player".center(8), "Record".center(15), "Gene".center(50)
#	print "="*25
#	for x in range(Rec.popsize):
#		print str(x).center(8), "".join([str(Rec.wins[x]),"-",
#										 str(Rec.losses[x]),"-",
#										 str(Rec.ties[x])]).center(15), str(Pop.population[x]).center(50)


def nextMove(board, players, turn1, Pop):

    #board.printBoard()
    #params determining the range of possible moves
    currBoard = board.nextBoard
    while currBoard == -1 or board.decided[currBoard] != -1:
        currBoard = random.randint(0,8)

    quotx = (currBoard % 3)
    quoty = (currBoard // 3)


    #if turn1 == True:
    #	gene = players.gene1
    #	winsBoard = board.winBoard1[currBoard]
    #
    #else
    #	gene = players.gene2
    #	winsBoard = board.winBoard2[currBoard]

    gene = players.genes[turn1]
    if len(gene) > 1:
        weight1 = gene[3] + 2
        weight2 = gene[9] + 2
        weight3 = gene[15] + 2
        sitweight = gene[20] + 2
    #print gene
    winsBoard = players.winBoard[currBoard][turn1]

    #dictionary of positional values
    posvals = {}

    #Lists of already-marked points
    selfmarked = []
    oppmarked = []
    possible = []
    for x in range(3 * quotx, 3 * quotx + 3):
        for y in range(3 * quoty, 3 * quoty + 3):
            if board.grid[x][y] == turn1:
                selfmarked.append((x,y))
            elif board.grid[x][y] == (not turn1):
                oppmarked.append((x,y))
            #mark possible moves for random player
            elif len(gene) == 1:
                possible.append((x,y))

    # portion that computes the values of each move
    posval = 0
    for x in range(3 * quotx, 3 * quotx + 3):
        if len(gene) == 1:
            break
        for y in range(3 * quoty, 3 * quoty + 3):
            if board.grid[x][y] > -1:
                continue

            #determine position of point in board
            #center (0), edge (1) , or corner (2)
            distfromorig = ( x - 3*quotx) + (y - 3*quoty)
            if distfromorig == 1 or distfromorig == 3: 		#edge
                #print (x, y), "is edge"
                posval = posval + weight1 * gene[1]
            elif distfromorig == 2 and (x - 3*quotx) == 1: 	#center
                #print (x, y), "is center"
                posval = posval + weight1 * gene[0]
            else: 											#corner
                #print (x, y), "is corner"
                posval = posval + weight1 * gene[2]

            #determine relative positions and
            #respective values to already marked points
            #shortdiag (0)
            #adjacent (1)
            #skip (2)
            #knight (3)
            #longdiag (4)
            for i,j  in selfmarked:
                distfrompt = (x - i) + (y - j)
                if distfrompt == 2:
                    if x != i and y != j:
                        distfrompt = 0

                posval = posval + weight2 * gene[players.offset + distfrompt]

            for p,q  in oppmarked:
                distfrompt = (x - p) + (y - q)
                if distfrompt == 2:
                    if x != p and y != q:
                        distfrompt = 0

                posval = posval + weight3 * gene[players.offset + players.oppoffset + distfrompt]

            # winning position of the board
            if (x,y) in winsBoard:
                posval = posval + sitweight * gene[16]

            #  block the opponent
            if (x,y) in players.winBoard[currBoard][not turn1]:
                posval = posval + sitweight * gene[17]

            # leading to a board which I can win
            tempNextBoard = (x - 3*quotx) + 3 * (y - 3*quoty)
            if len(players.winBoard[tempNextBoard][turn1]) > 0:
                posval = posval + sitweight * gene[18]

            # leading to a board which the opponent can win
            if len(players.winBoard[tempNextBoard][not turn1]) > 0:
                posval = posval + sitweight * gene[19]


            posvals[(x,y)] = posval
            posval = 0


    #print posvals
    SortedPosVals = sorted(posvals.iteritems(), key = operator.itemgetter(1), reverse = True)
    #print SortedPosVals
    toMark = (-1, -1)

    for coord, value in SortedPosVals:
        tempNextBoard = (coord[0] - 3*quotx) + 3 * (coord[1] - 3*quoty)
        #if board.decided[tempNextBoard] == -1:
        board.nextBoard = tempNextBoard
        board.grid[coord[0]][coord[1]] = turn1
        toMark = coord
        break

    #random player
    if len(gene) == 1:
        toMark = random.choice(possible)
        tempNextBoard = (toMark[0] - 3*quotx) + 3 * (toMark[1] - 3*quoty)
        board.nextBoard = tempNextBoard
        board.grid[toMark[0]][toMark[1]] = turn1


    if toMark == (-1, -1):
        #get the first key
        toMark = SortedPosVals[0][0]
        board.nextBoard = -1
        board.grid[toMark[0]][toMark[1]] = turn1

    # Check if the new move decide the board,
    # if not add (if any) possible deciding moves to the set
    if toMark in winsBoard:
        board.decided[currBoard] = turn1
        # there is a new decided board, check for win
        if (board.decided.count(turn1) + board.decided.count(2)) >= 3:
            indices = [i for i, x in enumerate(board.decided) if (x == turn1 or x == 2)]
            combos = [comb for comb in combinations(indices, 3)]
            for combo in combos:
                if combo in board.wincombos:
                    #Record
                    Pop[players.ids[turn1]].tempwins += 1
                    #Pop[players.ids[not turn1]].losses += 1
                    #board.printBoard()
                    #print str(players.ids[turn1]), "defeats", str(players.ids[not turn1]), "with boards", combo
                    return turn1

    else:
        #Check for a tied board
        if (len(selfmarked) + len(oppmarked)) == 8:
            board.decided[currBoard] = 2

        #Add possible deciding moves
        for marked in selfmarked:
            xdiff = abs(toMark[0] - marked[0])
            ydiff = abs(toMark[1] - marked[1])
            if (xdiff + ydiff) == 3:
                continue

            #bug here (should be fixed) we'll see
            tempx = min(marked[0], toMark[0]) + 3 - xdiff
            if tempx not in range(3*quotx, 3*quotx + 3):
                tempx = tempx -3
            tempy = min(marked[1], toMark[1]) + 3 - ydiff
            if tempy not in range(3*quoty, 3*quoty + 3):
                tempy = tempy -3

            if (abs(tempx - marked[0]) + abs(tempy - marked[1])) == 3:
                continue

            if (tempx, tempy) not in oppmarked:
                players.winBoard[currBoard][turn1].append((tempx, tempy))

    # Check for tie
    if board.decided.count(-1) == 0:
        #Record tie
        #Pop[players.ids[0]].ties += 1
        #Pop[players.ids[1]].ties += 1
        #board.printBoard()
        #print "Tie between", str(players.ids[0]), "and", str(players.ids[1])
        return 2

    #print str(currBoard), toMark, str(board.nextBoard)
    return -1

def game(Pop, p1, p2):
    gameBoard = Board()
    gamePlayers = Players(Pop, p1, p2)
    #print gamePlayers.genes

    #Process input genetic strings
    turn1 = True #true when it's Player1's turn, false otherwise
    gameover = -1

    while gameover < 0:
        gameover = nextMove(gameBoard, gamePlayers, turn1, Pop)
        turn1 = not turn1

def aggrecord(population, id1, id2):
    win1 = population[id1].tempwins
    win2 = population[id2].tempwins
    if win1 > win2:
        population[id1].wins += 1
        population[id2].losses += 1
    elif win1 < win2:
        population[id2].wins += 1
        population[id1].losses += 1
    elif win1 == win2:
        population[id1].ties += 1
        population[id2].ties += 1
    else:
        print "This doesn't make sense"
        exit(1)

    population[id1].tempwins = 0
    population[id2].tempwins = 0



def tournament(population, serieslen):
    popsize = len(population)

    #Integrate with Environment in example.py
    #Pop = Population(popsize)
    #Rec = Records(popsize)

    noofgames = serieslen
    for i in range(popsize):
        for j in range(popsize):
            if i == j:
                continue
            #gamePlayers = Players(Pop, i, j)
            while noofgames > 0:
                game(population, i, j)
                noofgames = noofgames - 1
            noofgames = serieslen
            aggrecord(population, i, j)

    #printRec(Rec, Pop)
    #TODO: use the records to perform crossover/mutation

