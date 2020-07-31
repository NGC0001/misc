'''
Calculate the GDP gini index according to a piece of news.
Assume exponential distribution.
'''

import numpy as np


def wealth_cumulated(population_cumulated, alpha):
    def fcum(x):
        return (np.exp(alpha*x) - 1) / (np.exp(alpha) - 1)
    return fcum(population_cumulated)


def wealth_perCapita(population_cumulated, alpha):
    def fcap(x):
        return (alpha*np.exp(alpha*x)) / (np.exp(alpha) - 1)
    return fcap(population_cumulated)


def gini(alpha):
    return (alpha*np.exp(alpha) - 2*np.exp(alpha) + alpha + 2) / (alpha*np.exp(alpha) - alpha)


# Data from the news.
lowerPopulation = 1.05  # billion people
lowerMeanGdp = 4.5  # k USD per capita
upperPopulation = 0.33  # billion people
upperMeanGdp = 25.  # k USD per capita

totalPopulation = lowerPopulation + upperPopulation
lowerGdp = lowerMeanGdp * lowerPopulation
upperGdp = upperMeanGdp * upperPopulation
totalGdp = lowerGdp + upperGdp


if __name__ == '__main__':
    x0 = lowerPopulation / totalPopulation
    y0 = lowerGdp / totalGdp
    a = 0.
    y = -1.
    for a1 in np.arange(4., 4.2, 0.001):
        y1 = wealth_cumulated(x0, a1)
        if np.abs(y1 - y0) < np.abs(y - y0):
            y = y1
            a = a1
    g = gini(a)
    print(f'a={a}, g={g}, y={y}, (x0={x0}, y0={y0}), [a1={a1}]')

