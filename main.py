import tsplib95 as tsp
import random
import math

problem = None

def fitnessFunction(tour):
  return sum(problem.get_weight(tour[i], 
                                tour[(i + 1) % len(tour)])
                                for i in range(len(tour)))

def deltaFitness(tour, lb, up):
  n = len(tour)

  i, j = tour[lb], tour[(lb + 1) % n]
  k, l = tour[up], tour[(up + 1) % n]

  old = problem.get_weight(i, j) + problem.get_weight(k, l)
  new = problem.get_weight(i, k) + problem.get_weight(j, l)

  return new - old

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

def precomputeNeighbors(tour, k=20):
  neighbors = {}

  for i in tour:
    distances = [(problem.get_weight(i, j), idx, j) for idx, j in enumerate(tour) if j != i]
    distances.sort()

    neighbors[i] = [(idx, j) for _, idx, j in distances[:k]]

  return neighbors

def twoOptLocalSearch(tour, k=20):
  best_tour = tour[:]
  best_fitness = fitnessFunction(best_tour)
  neighbors = precomputeNeighbors(best_tour, k)

  improved = True
  while improved:
    improved = False

    for i, node_id in enumerate(best_tour):
      for j, _ in neighbors[node_id]:
        if (
            abs(i - j) <= 1
            or (i == 0 and j == len(best_tour) - 1)
            or j <= i
        ):
          continue

        delta = deltaFitness(best_tour, i, j)
        if delta < 0:
          
          best_tour = (
            best_tour[:i+1] +
            best_tour[i+1:j+1][::-1] +
            best_tour[j+1:]
          )

          best_fitness += delta
          improved = True
          break

      if improved:
        break

  return best_tour


def singleImprovement(current, new):
    
    if fitnessFunction(new) < fitnessFunction(current):
        return new
    return current

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

def main():
  iterations = 10
  k = 15
  T = 500

  global problem
  problem = tsp.load('ALL_tsp/pcb442.tsp/pcb442.tsp')

  s = GenerateInitialSolution()
  print("Initial fitness:", fitnessFunction(s))

  s = twoOptLocalSearch(s, k)
  print("Fitness before the loop:", fitnessFunction(s))
 
  best = s

  for it in range(iterations):
    s_dash = doubleBridgePerturbation(s)
    s_dash = twoOptLocalSearch(s_dash, k)

    s = probabilisticAcceptance(s, s_dash, T)

    if fitnessFunction(s) < fitnessFunction(best):
      best = s

  print("Best fitness:", fitnessFunction(best))
  return best


if __name__ == "__main__":
  best_tour = main()
