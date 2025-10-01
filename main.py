import tsplib95 as tsp
import random

def GenerateInitialSolution(problem):
  nodes = list(problem.get_nodes())
  random.shuffle(nodes)

  return nodes

def doubleBridgePerturbation(tour):
    n = len(tour)

    if n <= 8:
       return tour
    
    idx = sorted(random.sample(range(n), 4))
    i, j, k, l = idx

    new_tour = []
    new_tour.extend(tour[:i])
    new_tour.extend(tour[k:l])
    new_tour.extend(tour[j:k])
    new_tour.extend(tour[i:j])
    new_tour.extend(tour[l:])

    return new_tour


if __name__ == "__main__":
  problem = tsp.load('ALL_tsp/pcb442.tsp/pcb442.tsp')  
  tour = GenerateInitialSolution(problem)
  print("Generisana tura (prvih 20 čvorova):", tour[:20])

  tour = doubleBridgePerturbation(tour)
