#!/usr/bin/env python
#*******************************************************************************
# utttsim.py
#
# Program to simulate a game of Ultimate Tic-Tac-Toe between two players of
# certain characteristics
# 
# Skeleton code from http://code.activestate.com/recipes/199121-a-simple-genetic-algorithm/
# Created by James Cheng
#*******************************************************************************
import operator
import random
import itertools

import tournament
import sys, getopt, time, datetime
import glob


# Class definitions

#MINIMIZE = 0

class Individual():
    alleles = (-1,0,1)
    length = 21
    seperator = ''
    #optimization = MINIMIZE

    def __init__(self, chromosome=None):
        self.chromosome = chromosome or self._makechromosome()
        #self.games = 0
        self.wins = 0
        self.ties = 0
        self.losses = 0
        self.tempwins = 0
        self.score = 0  # set during evaluation
    
    def _makechromosome(self):
        "makes a chromosome from randomly selected alleles."
        return [random.choice(self.alleles) for gene in range(self.length)]

    def evaluate(self, optimum=None):
        "this method MUST be overridden to evaluate individual fitness score."
        pass
    
    def crossover(self, other):
        "override this method to use your preferred crossover method."
        return self._twopoint(other)
    
    def mutate(self, gene):
        "override this method to use your preferred mutation method."
        self._pick(gene) 
    
    # sample mutation method
    def _pick(self, gene):
        "chooses a random allele to replace this gene's allele."
        self.chromosome[gene] = random.choice(self.alleles)
    
    # sample crossover method
    def _twopoint(self, other):
        "creates offspring via two-point crossover between mates."
        #left, right = self._pickpivots()
        left = 4
        center = 10
        right = 16
        def mate(p0, p1, type):
            chromosome = p0.chromosome[:]
            if type == 0:
                chromosome[0:left] = p1.chromosome[0:left]
            elif type == 1:
                chromosome[left:center] = p1.chromosome[left:center]
            elif type == 2:
                chromosome[center:right] = p1.chromosome[center:right]
            elif type == 3:
                chromosome[right:] = p1.chromosome[right:]
            child = p0.__class__(chromosome)
            child._repair(p0, p1)
            return child
        
        offspring = []
        for x in range(4):
            offspring.append(mate(self, other, x))
            offspring.append(mate(other, self, x))
        
        return offspring

    # some crossover helpers ...
    def _repair(self, parent1, parent2):
        "override this method, if necessary, to fix duplicated genes."
        pass

    def _pickpivots(self):
        left = random.randrange(1, self.length-2)
        right = random.randrange(left, self.length-1)
        return left, right

    #
    # other methods
    #

    def __repr__(self):
        "returns string representation of self"
        return '<%s chromosome="%s" score=%s>' % \
               (self.__class__.__name__,
                self.seperator.join(map(str,self.chromosome)), self.score)

    #def __cmp__(self, other):
    #    if self.optimization == MINIMIZE:
    #        return cmp(self.score, other.score)
    #    else: # MAXIMIZE
    #        return cmp(other.score, self.score)
    
    def copy(self):
        twin = self.__class__(self.chromosome[:])
        twin.score = self.score
        return twin


class Environment():
    def __init__(self, kind, population=None, size=100, maxgenerations=500, 
                 crossover_rate=0.90, mutation_rate=0.10, optimum=None, threshold=50, serieslen = 7, genbest = None):
        self.kind = kind
        self.size = size
        self.optimum = optimum
        self.population = population or self._makepopulation()
        #for individual in self.population:
        #    individual.evaluate(self.optimum)
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.maxgenerations = maxgenerations
        self.generation = 0
        self.serieslen = serieslen
        self.threshold = threshold
        self.prevbest = []
        self.counter = 0
        self.genbest = genbest or [] #list of best chromosomes across generations
        #self.report()

    def _makepopulation(self):
        return [self.kind() for individual in range(self.size)]
    
    def run(self):
        while not self._goal():
            self.step()
        print "Entering Benchmark Comparison"
        self.benchmarkcomp()
        return self.genbest
    
    def benchmarkcomp(self):
        population = []
        population.append(UltimateTTT(chromosome = self.prevbest))
        if len(self.genbest) == 0:
            population.append(UltimateTTT(chromosome = [0]))
        else:
            index = len(self.genbest) - 1
            population.append(UltimateTTT(chromosome = self.genbest[index]))
        for x in xrange(500):
            tournament.tournament(population, self.serieslen)

        self.report(pop = population)
    	
    
    def _goal(self):
        return self.generation > self.maxgenerations or \
               self.counter >= self.threshold
    
    def step(self):
        self.play()
        self.generation += 1
        self.report()
        self._crossover()

        
    def _crossover(self):
        next_population = []
        top5percent = self.size // 20
        for x in range(top5percent):
            next_population.append(self.population[x])
        while len(next_population) < self.size:
            mate1 = self._select()
            if random.random() < self.crossover_rate:
                mate2 = self._select()
                offspring = mate1.crossover(mate2)
            else:
                offspring = [mate1.copy()]
            for individual in offspring:
                self._mutate(individual)
                #individual.evaluate(self.optimum)
                next_population.append(individual)
        self.population = next_population[:self.size]
        #self.population = list(set(self.population))
        #while len(next_population) < self.size:
        #    new = Individual()
        	
        #reset records
        for i in self.population:
            i.wins = 0
            i.ties = 0
            i.losses = 0
            i.score = 0
        

    def _select(self):
        "override this to use your preferred selection method"
        cutoff = self.size // 2
        index = random.randint(0, self.size) 
        while index > cutoff:
            index = random.randint(0, self.size)
        return self.population[index]
    
    def _mutate(self, individual):
        for gene in range(individual.length):
            if random.random() < self.mutation_rate:
                individual.mutate(gene)
                
    def play(self):
        tournament.tournament(self.population, self.serieslen)


    #
    # sample selection method
    #
    #def _tournament(self, size=8, choosebest=0.90):
    #    competitors = [random.choice(self.population) for i in range(size)]
    #    competitors.sort()
    #    if random.random() < choosebest:
    #        return competitors[0]
    #    else:
    #        return random.choice(competitors[1:])
    
    def best(self):

        for player in self.population:
            player.evaluate()

        self.population.sort(key=operator.attrgetter("score"), reverse = True)

        return self.population[0]

    def report(self, pop = None):

        population = pop or self.population

        for player in population:
            player.evaluate()
        population.sort(key=operator.attrgetter("score"), reverse = True)

        if len(population) == 2:
            self.genbest.append(population[0].chromosome)
        else:
            if population[0].chromosome == self.prevbest:
                self.counter += 1
            else:
                self.counter = 0
            self.prevbest = population[0].chromosome

        #if len(population) < self.size or self.counter > (self.threshold - 3):
        print "="*70
        print "generation: ", self.generation
        print "counter: ", self.counter
        print "time: ", datetime.datetime.now()
        print "Player".center(8), "Record".center(15), "Gene".center(50)
        print "="*25
        for i in population:
            print str(population.index(i)).center(8), "".join([str(i.wins),"-",
                               str(i.losses),"-",
                               str(i.ties)]).center(15), str(i.chromosome).center(50)
								
        #print "best:       ", self.best


class UltimateTTT(Individual):

    #optimization = genetic.MAXIMIZE 
    def evaluate(self, optimum=None):
        self.score = self.wins - self.losses

   
if __name__ == "__main__":
    for x in xrange(5):
        currtime = datetime.datetime.now()
        currtimeStr = datetime.datetime.strftime(currtime, "%m%d%H%M")
        respath = "sim" + currtimeStr + ".txt"
        sys.stdout = open(respath, 'w')

        print "Simulation", str(x)
        print "time: ", currtime

        genbest = []
        for n in xrange(5):
            env = Environment(UltimateTTT, size=40, maxgenerations=80, threshold=4, genbest = genbest)
            genbest = env.run()

        elitepop = []

        elites = list(genbest for genbest,_ in itertools.groupby(genbest))
        for best in elites:
            print "Result", str(elites.index(best)), ":", best
            elitepop.append(UltimateTTT(chromosome=best))

        number = 500 // (len(elites) - 1)
        for x in xrange(number):
            tournament.tournament(elitepop, 7)

        eliteenv = Environment(UltimateTTT, population=elitepop)
        eliteenv.report()


    
#other feats
# winning position of the board
# block the opponent
# leading to a board which the opponent can win
# leading to a board which I can win
# new benchmark?
