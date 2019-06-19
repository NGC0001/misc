## Transformation between Legendre polynomials,
## Chebyshev polynomials, and Power series.


import math
from fractions import Fraction
import numpy as np
import functools, itertools


##############################
# P: Legendre polynomials
# T: Chebyshev polynomials
# X: powers
##############################


def matrix_P_to_X(n):
    assert type(n) is int
    assert n >= 0

    m = np.full((n+1,n+1), Fraction(0))
    m[0,0] = Fraction(1)

    if n > 0:
        m[1,1] = Fraction(1)

        for j in range(2, n+1):
            m[1:, j] += m[:-1, j-1] * Fraction(2*j-1, j)
            m[:, j] -= m[:, j-2] * Fraction(j-1, j)

    return m


def P_in_terms_of_X(n):
    assert type(n) is int
    assert n >= 0

    m = matrix_P_to_X(n)
    return m[:,n].copy()


##############################


## http://mathworld.wolfram.com/LegendrePolynomial.html

def X_in_terms_of_P(n):
    assert type(n) is int
    assert n >= 0

    v = np.full(n+1, Fraction(0))

    v[-1::-2] = Fraction(math.factorial(n))

    for l in range(n, -1, -2):
        v[l] *= 2 * l + 1
        v[l] /= 2 ** ((n-l)//2)
        v[l] /= math.factorial((n-l)//2)
        v[l] /= functools.reduce(int.__mul__, range(n+l+1, 0, -2))

    return v


def matrix_X_to_P(n):
    assert type(n) is int
    assert n >= 0

    m = np.full((n+1,n+1), Fraction(0))

    for i in range(n+1):
        m[:i+1, i] = X_in_terms_of_P(i)

    return m


##############################


## https://en.wikipedia.org/wiki/Chebyshev_polynomials

def matrix_T_to_X(n):
    assert type(n) is int
    assert n >= 0

    m = np.full((n+1,n+1), Fraction(0))
    m[0,0] = Fraction(1)

    if n > 0:
        m[1,1] = Fraction(1)

        for j in range(2, n+1):
            m[1:, j] += m[:-1, j-1] * 2
            m[:, j] -= m[:, j-2]

    return m


def T_in_terms_of_X(n):
    assert type(n) is int
    assert n >= 0

    m = matrix_T_to_X(n)
    return m[:,n].copy()


##############################


def inverse_upper_triangular_matrix(m):
    assert len(m.shape) == 2
    n = m.shape[0]
    assert n > 0
    assert m.shape[1] == n

    mr = np.full((n,n), Fraction(0))
    for i in range(n):
        mr[i, i] = Fraction(1)

    for i in range(n-1, -1, -1):
        for j in range(i-1, -1, -1):
            mr[j,:] -= mr[i,:] * (m[j,i] / m[i,i])
        mr[i,:] /= m[i,i]

    return mr


def matrix_X_to_T(n):
    assert type(n) is int
    assert n >= 0

    m = matrix_T_to_X(n)
    mr = inverse_upper_triangular_matrix(m)

    return mr


def X_in_terms_of_T(n):
    assert type(n) is int
    assert n >= 0

    m = matrix_X_to_T(n)
    return m[:,n].copy()


##############################


def matrix_P_to_T(n):
    assert type(n) is int
    assert n >= 0

    pToX = matrix_P_to_X(n)
    xToT = matrix_X_to_T(n)

    m = np.full((n+1,n+1), Fraction(0))
    for i, j, k in itertools.product(range(n+1), range(n+1), range(n+1)):
        m[i, j] += xToT[i, k] * pToX[k, j]

    return m


def P_in_terms_of_T(n):
    assert type(n) is int
    assert n >= 0

    m = matrix_P_to_T(n)
    return m[:,n].copy()


##############################


def matrix_T_to_P(n):
    assert type(n) is int
    assert n >= 0

    tToX = matrix_T_to_X(n)
    xToP = matrix_X_to_P(n)

    m = np.full((n+1,n+1), Fraction(0))
    for i, j, k in itertools.product(range(n+1), range(n+1), range(n+1)):
        m[i, j] += xToP[i, k] * tToX[k, j]

    return m


def T_in_terms_of_P(n):
    assert type(n) is int
    assert n >= 0

    m = matrix_T_to_P(n)
    return m[:,n].copy()


##############################


def factorial2(n):
    if n <= 1:
        return Fraction(1)
    else:
        return Fraction(n) * factorial2(n-2)


