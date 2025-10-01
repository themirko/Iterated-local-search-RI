import tsplib95 as tsp
import matplotlib.pyplot as plt
import random
import time
import math
import threading

#-------------------------------------------------------------------------------

problem = None
iterations = 0
best_valuesSI = []
best_valuesPA = []

#-------------------------------------------------------------------------------

def fitnessFunction(tour):
  return sum(problem.get_weight(tour[i], 
                                tour[(i + 1) % len(tour)])
                                for i in range(len(tour)))

def deltaFitness(tour, lb, ub):
  n = len(tour)

  i, j = tour[lb], tour[(lb + 1) % n]
  k, l = tour[ub], tour[(ub + 1) % n]

  old = problem.get_weight(i, j) + problem.get_weight(k, l)
  new = problem.get_weight(i, k) + problem.get_weight(j, l)

  return new - old

#-------------------------------------------------------------------------------

def GenerateInitialSolution():
  nodes = list(problem.get_nodes())
  random.shuffle(nodes)

  return nodes

#-------------------------------------------------------------------------------

def doubleBridgePerturbation(tour):
  n = len(tour)
  if n <= 8:
    return tour

  i, j, k, l = sorted(random.sample(range(n), 4))
  return tour[:i] + tour[k:l] + tour[j:k] + tour[i:j] + tour[l:]

#-------------------------------------------------------------------------------

def precomputeNeighbors(tour, k=20):
  neighbors = {}

  for i in tour:
    distances = ([(problem.get_weight(i, j), idx, j) 
                 for idx, j in enumerate(tour) 
                 if j != i])

    distances.sort()

    neighbors[i] = [(idx, j) for _, idx, j in distances[:k]]

  return neighbors

#-------------------------------------------------------------------------------

def twoOptLocalSearch(tour, k=20):
  global iterations

  best_tour = tour[:]
  best_fitness = fitnessFunction(best_tour)
  neighbors = precomputeNeighbors(best_tour, k)

  improved = True
  while improved:
    improved = False
    iterations += 1

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

#-------------------------------------------------------------------------------

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

#-------------------------------------------------------------------------------

def plot_progress():
    plt.figure(figsize=(8, 5))
    
    plt.plot(range(len(best_valuesSI)),
             best_valuesSI,
             marker='o',
             markersize=3,
             linewidth=1,
             label="Single Acceptence",
             color="blue")
    
    plt.plot(range(len(best_valuesPA)),
             best_valuesPA,
             marker='x',
             markersize=3,
             linewidth=1,
             label="Probabilistic Acceptance",
             color="red")
    
    plt.xlabel("Iterations")
    plt.ylabel("Best value per iteration")
    plt.title("Progress per iteration")
    plt.grid(True)
    plt.legend()
    plt.show()

#-------------------------------------------------------------------------------

def IteratedLocalSearch(problem_name, acceptence):
  global iterations
  global best_values
  global problem

  k = 25
  T = 500
  MAX_TIME = 120  # sekunde

  problem = tsp.load(f'ALL_tsp/{problem_name}.tsp/{problem_name}.tsp')
  optimal = tsp.load(f'ALL_tsp/{problem_name}.opt.tour/{problem_name}.opt.tour')
  
  optimal_fitness = fitnessFunction(optimal.tours[0])

  s = GenerateInitialSolution()
  fitness = fitnessFunction(s)
  (best_valuesSI if acceptence else best_valuesPA).append(fitness)

  s = twoOptLocalSearch(s, k)
  fitness = fitnessFunction(s)
  (best_valuesSI if acceptence else best_valuesPA).append(fitness)

  best = s

  start = time.time()
  
  while time.time() - start < MAX_TIME:
    s_dash = doubleBridgePerturbation(s)
    s_dash = twoOptLocalSearch(s_dash, k)

    if acceptence:
      s = singleImprovement(s, s_dash)
    else:
      s = probabilisticAcceptance(s, s_dash, T)

    fitness = fitnessFunction(s)
    if fitness < fitnessFunction(best):
      (best_valuesSI if acceptence else best_valuesPA).append(fitness)
      best = s

  best_fitness = fitnessFunction(best)
  print(
    f"Ran for {int(time.time() - start)} seconds\n"
    f"and {iterations} iterations")

  error = (best_fitness - optimal_fitness) / optimal_fitness * 100
  print(f"Error ({'Single Improvement' if acceptence 
                                       else 'Probabilistic Acceptance'}):" 
                                       f"{error:.2f}%")

#-------------------------------------------------------------------------------

def main():
  # 1 == Single Improvement
  # 0 == Probabilistic Acceptance
  t1 = threading.Thread(target=IteratedLocalSearch, args=("kroA100", 1))
  t2 = threading.Thread(target=IteratedLocalSearch, args=("kroA100", 0))

  t1.start()
  t2.start()

  t1.join()
  t2.join()

  plot_progress()


#-------------------------------------------------------------------------------

if __name__ == "__main__":
  main()
