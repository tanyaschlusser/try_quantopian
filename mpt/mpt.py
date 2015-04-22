# -*- coding: utf-8 -*-#
"""
mpt.py

Implements the modern portfolio theory.
"""
import math
import numpy as np
import pandas as pd

from numpy.linalg import inv as invert
from scipy.optimize import minimize

def _get_efficient_frontier(
        expected_values, standard_deviations, covariances,
        returns = [x * 0.25 / 42 for x in range(42)]):
    cov_inv = invert(covariances)
    A = sum(sum(cov_inv))
    B = sum(np.dot(cov_inv, expected_values))
    C = np.dot(expected_values.transpose(),
                np.dot(cov_inv, expected_values))
    D = A * C - B**2
    risks = [math.sqrt((A / D) * r**2 - (2 * B / D) * r + C / D) 
                  for r in returns]
    return pd.DataFrame({
            'returns' : [r for r in returns],
            'risks' : [r for r in risks]})

    
def get_efficient_frontier(df, annualized=False):
    """Get the best risks for the target return
    """
    expected_values  = np.array([df.mean()]).transpose()
    standard_deviations = np.array([df.std()]).transpose()
    covariances = df.cov()
    N = len(expected_values)

    if not annualized:
        days_in_year = 260
        expected_values  = ((1+expected_values) ** days_in_year) - 1
        standard_deviations = standard_deviations * math.sqrt(days_in_year)
        covariances = covariances * days_in_year

    return _get_efficient_frontier(
            expected_values, standard_deviations, covariances)
    

def get_portfolio(df, returns, lb=0, ub=1):
    """Get the best portfolio given the specified returns.

    lb, ub are scalars or a vector with the same length as the number
    of possible stocks in the portfolio.

    lb = 0 means you cannot short a stock
    ub = 1 means you have 100% of your portfolio in one stock

    usually people fix the lb = 0 or lb = - 0.05 (no more than 5% shorted
    per stock) and set ub for treasury bills to be like 0.03 or something.
    """
    ncol = df.shape()[1]
    expected_values  = df.mean()
    covariances = df.cov()
    H = invert(covariances)
    lower = lb if hasattr(lb, '__iter__') else [lb] * ncol
    upper = ub if hasattr(ub, '__iter__') else [ub] * ncol
    returns = returns if hasattr(returns, '__iter__') else [returns]
    bounds = zip(lower, upper)

    def objective(x):
        """Goal is to minimize 1/2 * x' H x; drop the 1/2."""
        return np.transpose(x).dot(H.dot(x))

    def gradient(x):
        return np.transpose(x).dot(np.multiply(
                H,
                (np.ones((ncol,ncol)) + np.eye(ncol))))

    initial_guess = np.ones(ncol) / ncol

    allocations = []
    risks = []
    for r in returns:
        # Constraint is A x = b ==> A x - b = 0
        #
        # First constraint is sum(x) = 1 so portfolio totals to 100%
        # The next constraint is the target return --
        #  sum(x * expected_values) = target_return
        #
        #  A = [1 1 1    b = [1
        #       1 1 1]        desired_return ]
        #
        #
        # --> so ...  A x = b   becomes   A x - b = 0
        #
        #   A           x          b
        #   [1  1  1    [x1    -   [1                 =  [0
        #    e1 e2 e3]   x2         desired_return]       0]
        #                x3]
        #
        # xi = the percent allocation of each stock in the portfolio
        # ei = the expected return for a given stock
        # 
        #     x1 +    x2 +    x3 = 1              (portfolio 100%)
        #  e1 x1 + e2 x2 + e3 x3 = desired_return (expected return is as desried)
        #
        A = np.array(np.ones((2, ncol)))
        A[:,:-1] = expected_values
        b = np.array([[1.],[r]])
        constraints = dict(type='eq', fun=lambda x: A.dot(x) - b)

        result = minimize(objective, initial_guess, method='SLSQP',
                jac=gradient, bounds=bounds, constraints=constraints)

        
        allocations.append(list(result.x) if result.success else [np.nan] * ncol)
        risks.append(result.x.dot(covariances.dot(result.x)))

    result = np.zeros((len(returns), ncol + 2))
    result[:,0] = returns
    result[:,1] = risks
    result[:,2:] = np.array(allocations)
    return pd.DataFrame(result, columns = ["returns", "risks"] + list(df.names))

