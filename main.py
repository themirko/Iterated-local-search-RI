import tsplib95 as tsp
import random

def fitnessFunction(tour, problem):
  return sum(problem.get_weight(tour[i], 
                                tour[(i + 1) % len(tour)])
                                for i in range(len(tour)))

def GenerateInitialSolution(problem):
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

if __name__ == "__main__":
  problem = tsp.load('ALL_tsp/pcb442.tsp/pcb442.tsp')
  tour = GenerateInitialSolution(problem)

  print("Generisana tura (prvih 20 čvorova):", tour[:20])
  print("Dužina inicijalne ture:", fitnessFunction(tour, problem))

  tour = doubleBridgePerturbation(tour)
  print("Dužina posle perturbacije:", fitnessFunction(tour, problem))
