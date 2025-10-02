import tsplib95 as tsp
import matplotlib.pyplot as plt
import random
import time
import math

#-------------------------------------------------------------------------------
random.seed(47)

problem = None
start_time = None

iterations = 0
MAX_TIME = 160  # sekunde

best_valuesSI = []
best_valuesPA = []

optimal_fitness = {
    "kroA100": 21282,
    "d198": 15780,
    "lin318": 42029,
    "pcb442": 50778,
    "rat783": 8806,
    "pr1002": 259045,
    "pcb1173": 56892,
    "d1291": 50801,
    "fl1577": 22249,
    "pr2392": 378032,
    "pcb3038": 137694,
    "fl3795": 28772,
    "rl5915": 565530
}

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

def segmentShufflePerturbation(tour, minL=3):
  n = len(tour)
  if n < minL:
    return tour
  
  maxL = max(5, n // 20)
  segL = random.randint(minL, min(maxL, n))

  start = random.randint(0, n - segL)
  end = start + segL

  prefix = tour[:start]
  segment = tour[start:end]
  suffix = tour[end:]

  random.shuffle(segment)
  
  return prefix + segment + suffix

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
  global start_time

  best_tour = tour[:]
  best_fitness = fitnessFunction(best_tour)
  neighbors = precomputeNeighbors(best_tour, k)

  improved = True
  while improved and (time.time() - start_time < MAX_TIME):
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

#-------------------------------------------------------------------------------

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
  global problem
  global start_time
  global MAX_TIME

  k = 25
  T = 920   
  iterations = 0

  problem = tsp.load(f'ALL_tsp/{problem_name}.tsp/{problem_name}.tsp')
  
  s = GenerateInitialSolution()
  fitness = fitnessFunction(s)
  (best_valuesSI if acceptence else best_valuesPA).append(fitness)

  start_time = time.time()

  s = twoOptLocalSearch(s, k)
  fitness = fitnessFunction(s)
  (best_valuesSI if acceptence else best_valuesPA).append(fitness)

  best = s

  while time.time() - start_time < MAX_TIME:
    # for ii in range(3):
    s_dash = segmentShufflePerturbation(s)
    s_dash = twoOptLocalSearch(s_dash, k)

    if acceptence:
      s = singleImprovement(s, s_dash)
    else:
      s = probabilisticAcceptance(s, s_dash, T)
      T *= 0.99

    fitness = fitnessFunction(s)
    (best_valuesSI if acceptence else best_valuesPA).append(fitness)

    if fitness < fitnessFunction(best):
      best = s

  best_fitness = fitnessFunction(best)
  print(
    f"Ran for {int(time.time() - start_time)} seconds\n"
    f"and {iterations} iterations")

  error = ((best_fitness - optimal_fitness[problem_name]) / 
            optimal_fitness[problem_name] * 100)
  
  print(f"Error ({'Single Improvement' if acceptence 
                                       else 'Probabilistic Acceptance'}):" 
                                       f"{error:.2f}%")

#-------------------------------------------------------------------------------

def main():
  # 1 == Single Improvement
  # 0 == Probabilistic Acceptance
  IteratedLocalSearch("kroA100", 1)  # Single Improvement
  IteratedLocalSearch("kroA100", 0)  # Probabilistic Acceptance


  plot_progress()


#-------------------------------------------------------------------------------

if __name__ == "__main__":
  main()
