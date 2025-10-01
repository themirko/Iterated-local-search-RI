import tsplib95 as tsp
import random
import math

problem = None

def fitnessFunction(tour):
  return sum(problem.get_weight(tour[i], 
                                tour[(i + 1) % len(tour)])
                                for i in range(len(tour)))

def GenerateInitialSolution():
  nodes = list(problem.get_nodes())
  random.shuffle(nodes)

  return nodes

def doubleBridgePerturbation(tour):
  n = len(tour)
  if n <= 8:
    return tour

  i, j, k, l = sorted(random.sample(range(n), 4))
  return tour[:i] + tour[k:l] + tour[j:k] + tour[i:j] + tour[l:]

def twoOptLocalSearch(tour):
  n = len(tour)
  
  best_tour = tour
  best_fitness = fitnessFunction(best_tour)

  for i in range(1, n-1):
    for j in range(i+2, n):

      new_tour = tour[:i] + tour[i:j][::-1] + tour[j:]
      new_fitness = fitnessFunction(new_tour)

      if new_fitness < best_fitness:
        return new_tour

  return best_tour

#local search prvi nacin
def singleImprovement(current, new):
    
    if fitnessFunction(new) < fitnessFunction(current):
        return new
    return current

#drugi nacin - simulated annealing style, probabilistic acceptance
def probabilisticAcceptance(current, new, T):
    
    currFitness = fitnessFunction(current)
    newFitness = fitnessFunction(new)

    if newFitness < currFitness:
        return new
    
    diff = newFitness - currFitness
    x = math.exp(-diff/T)
    if random.random() < x:
        return new
    
    return current

if __name__ == "__main__":
    problem = tsp.load('ALL_tsp/pcb442.tsp/pcb442.tsp')

    tour = GenerateInitialSolution()  # bez argumenta

    print("Generisana tura (prvih 20 čvorova):", tour[:20])
    print("Dužina inicijalne ture:", fitnessFunction(tour))  # samo tour

    new_tour = doubleBridgePerturbation(tour)
    print("Dužina posle perturbacije:", fitnessFunction(new_tour))  # samo tour

    #LOCAL SEARCH 
    bestResult = singleImprovement(tour, new_tour)  # bez problem

    T = 500
    alpha = 0.01

    bestResult = probabilisticAcceptance(tour, new_tour, T);

    T = T * alpha #ovo ce ici unutar whilea
    print("Najbolji rezultat je ", bestResult)
