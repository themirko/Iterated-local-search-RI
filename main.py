import tsplib95 as tsp
import matplotlib.pyplot as plt
import random
import time
import math

#-------------------------------------------------------------------------------
random.seed(47)

problem_name = ""
problem = None
start_time = None

iterations = 0
T = 920  
MAX_TIME = 180  # sekunde

best_values1 = []
best_values2 = []

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

  return best_tour, best_fitness

#-------------------------------------------------------------------------------

def singleImprovement(current, new):
    
    currFitness = fitnessFunction(current)
    newFitness = fitnessFunction(new)

    if newFitness < currFitness:
        return new, newFitness
    
    return current, currFitness

#-------------------------------------------------------------------------------

def probabilisticAcceptance(current, new):
    
    currFitness = fitnessFunction(current)
    newFitness = fitnessFunction(new)

    if newFitness < currFitness:
        return new, newFitness
    
    diff = newFitness - currFitness
    x = math.exp(-diff/T)
    if random.random() < x:
        return new, newFitness
    
    return current, currFitness

#-------------------------------------------------------------------------------

def plot_progress(label1, label2):
    plt.figure(figsize=(16, 9))
    
    plt.axhline(y=optimal_fitness[problem_name],
            color='green',
            linewidth=1.5,
            zorder=0)

    plt.plot(range(len(best_values1)),
            best_values1,
            linewidth=1.5,
            label=label1,
            color="blue")

    plt.plot(range(len(best_values2)),
            best_values2,
            linewidth=1.5,
            label=label2,
            color="red")
    
    plt.yscale('log')
    plt.xlabel("Iterations")
    plt.ylabel("Best value per iteration")
    plt.title(f"Progress per iteration for TSP: {problem_name}")
    plt.grid(True)
    plt.legend()
    plt.show()

#-------------------------------------------------------------------------------

def IteratedLocalSearch(acceptenceF, localsearchF, perturbationF):
  global iterations
  global T
  global problem
  global start_time
  global MAX_TIME

  best_values= []

  k = 65 
  T = 920   
  iterations = 0

  s = GenerateInitialSolution()
  fitness = fitnessFunction(s)
  best_values.append(fitness)

  start_time = time.time()

  s, best_fitness = localsearchF(s, k)
  best_values.append(best_fitness)

  while time.time() - start_time < MAX_TIME:
    s_dash = perturbationF(s)
    s_dash, _ = localsearchF(s_dash, k)

    s, fitness = acceptenceF(s, s_dash)
    T *= 0.99

    best_values.append(fitness)

    if fitness < best_fitness:
      best_fitness = fitness

  print(
    f"Ran for {int(time.time() - start_time)} seconds\n"
    f"and {iterations} iterations")

  error = ((best_fitness - optimal_fitness[problem_name]) / 
            optimal_fitness[problem_name] * 100)
  
  print(f"Error {error:.2f}%")

  return best_values

#-------------------------------------------------------------------------------

def main():
  
  global problem_name
  global problem

  global best_values1
  global best_values2

  problem_name = "rat783"
  problem = tsp.load(f'ALL_tsp/{problem_name}.tsp/{problem_name}.tsp')

  
  best_values1 = IteratedLocalSearch(singleImprovement, 
                                     twoOptLocalSearch,
                                     doubleBridgePerturbation)
  
  best_values2 = IteratedLocalSearch(probabilisticAcceptance, 
                                     twoOptLocalSearch,
                                     doubleBridgePerturbation)

  plot_progress("Single Improvement", "Probabilistic Acceptance")
  # plot_progress("Double Bridge", "Segment Shuffle")



#-------------------------------------------------------------------------------

if __name__ == "__main__":
  main()
