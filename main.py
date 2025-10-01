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

def precomputeNeighbors(tour, problem, k=20):
  neighbors = {}

  for i in tour:
    distances = [(problem.get_weight(i, j), idx, j) for idx, j in enumerate(tour) if j != i]
    distances.sort()

    neighbors[i] = [(idx, j) for _, idx, j in distances[:k]]

  return neighbors

def twoOptLocalSearch(tour, problem, k=20):
  best_tour = tour[:]
  best_fitness = fitnessFunction(best_tour, problem)

  improved = True
  while improved:
    improved = False
    neighbors = precomputeNeighbors(best_tour, problem, k)

    for i, node_i in enumerate(best_tour):
      for j_idx, _ in neighbors[node_i]:
        
        if (
            abs(i - j_idx) <= 1
            or (i == 0 and j_idx == len(best_tour) - 1)
            or j_idx <= i
        ):
          continue

        candidate = (
          best_tour[:i+1] + best_tour[i+1:j_idx+1][::-1] + best_tour[j_idx+1:])
        candidate_fitness = fitnessFunction(candidate, problem)

        if candidate_fitness < best_fitness:
          best_tour = candidate
          best_fitness = candidate_fitness
          improved = True
          break

      if improved:
        break

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
  problem = tsp.load('ALL_tsp/burma14.tsp/burma14.tsp')
  tour = GenerateInitialSolution(problem)

  print("Generisana tura (prvih 20 čvorova):", tour[:20])
  print("Dužina inicijalne ture:", fitnessFunction(tour))  # samo tour

  tour = doubleBridgePerturbation(tour)
  print("Dužina posle perturbacije:", fitnessFunction(tour, problem))

  best_tour = twoOptLocalSearch(tour, problem)

  print("Dužina posle perturbacije:", fitnessFunction(best_tour, problem))
