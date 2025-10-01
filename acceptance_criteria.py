import math
import random
from utils import fitnessFunction

#prvi nacin - greedy acceptance
#problem: glavi se u lokalnim min
def singleImprovement(current, new, problem):
    
    if fitnessFunction(new, problem) < fitnessFunction(current, problem):
        return new
    return current

#drugi nacin - simulated annealing style, probabilistic acceptance
def probabilisticAcceptance(current, new, problem, T):
    
    currFitness = fitnessFunction(current, problem)
    newFitness = fitnessFunction(new, problem)

    if newFitness < currFitness:
        return new
    
    diff = newFitness - currFitness
    x = math.exp(-diff/T)
    if random.random() < x:
        return new
    
    return current

#unutar glavne petlje treba da smanjujem temp za faktor hladjenja

