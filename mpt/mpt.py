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
        returns = [x * 0.15 / 42 for x in range(42)]):
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
        days_in_year = 250
        expected_values  = expected_values * days_in_year
        standard_deviations = standard_deviations * days_in_year
        covariances = covariances * days_in_year * days_in_year

    return _get_efficient_frontier(
            expected_values, standard_deviations, covariances)
    

def get_portfolio(df, returns, lb=0, ub=1):
    """Get the best portfolio given the specified returns.
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

    risks = []
    for r in returns:
        # Constraint is A x = b ==> A x - b = 0
        # First constraint is sum(x) = 1 so portfolio totals to 100%
        # The next constraint is the target return --
        #  sum(x * expected_values) = target_return
        A = np.array(np.ones((2,ncol)))
        A[:,:-1] = expected_values
        b = np.array([[1.],[r]])
        constraints = dict(type='eq', fun=lambda x: A.dot(x) - b)

        result = minimize(objective, initial_guess, method='SLSQP',
                jac=gradient, bounds=bounds, constraints=constraints)

        risks.append(result.x if result.success else np.nan)

    return pd.DataFrame(dict(returns=returns, risks=risks))

