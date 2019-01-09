"""
Authors: Vitor Eller (@Vfermat) and Liam Dunphy (@ldunphy98)
"""

import matplotlib.pyplot as plt
import numpy as np

from scipy.interpolate import interp1d

class SwapCurve(object):
    
    interpolate_display = {
            'linear': 'r-',
            'cubic': 'g--',
            'quadratic': 'b:',
            'nearest': 'y-.'            
            }
    
    def __init__(self, rates, convention):
        """
        convention options:
            business_days
            calendar_days
        rates options:
            pandas dataframe
        """
        self.convention = convention
        self.rates = rates
        
    def plot_day_curve(self, dates, interpolate=False, interpolate_methods=None):
        """
        TO DO:
            - implement algorithm that lets the user pick any date, even if we don't have
            that specific curve
            - Change de xlabel to the term, instead of letting it show 'days to maturity'
        """
        # Checking Inputs
        if type(dates) is not list:
            raise TypeError("Argument 'dates' should be a list.")
        if type(interpolate_methods) is not list and interpolate_methods is not None:
            raise TypeError("If you desire to interpolate, argument 'interpolate_method' should be a list")
            
        # Gathering curves information.
        curves = []
        for date in dates:
            try:
                curve = self.rates[date]
                curve = curve.dropna()
            except IndexError as e:
                print('{}. {} is an invalid date. It will not be used.'.format(e, date))
            else:
                curves.append(curve)
                
        # Check if there are curves to be plotted (or all dates where invalid)
        if len(curves) == 0:
            raise ValueError('There are no dates to be plotted.')
            
        plotted = False
        # Start plotting
        for curve in curves:
            date = curve.name
            if interpolate:
                if len(interpolate_methods) == 1:
                    terms = curve.index
                    dterms = [self._days_in_term(t, self.convention) for t in terms]
                    iterms = np.arange(min(dterms), max(dterms), 10)
                    irates = self._interpolate_rates(dterms, list(curve), iterms, interpolate_methods[0])
                    plt.plot(iterms, irates, label=date)
                    plt.legend()
                    plt.xlabel('Days to Maturity')
                    plt.ylabel('Swap Rate (%)')
                else:
                    terms = curve.index
                    dterms = [self._days_in_term(t, self.convention) for t in terms]
                    iterms = np.arange(min(dterms), max(dterms), 10)
                    for method in interpolate_methods:
                        plot_type = self.interpolate_display[method]
                        irates = self._interpolate_rates(dterms, list(curve), iterms, method)
                        plt.plot(iterms, irates, plot_type, label=method)
                    plt.xlabel('Days to Maturity')
                    plt.ylabel('Swap Rate (%)')
                    plt.title(date)
                    plt.legend()
                    plt.show()
                    plotted = True
            else:
                curve.plot(label=date)
        
        if not plotted:
            plt.xlabel('Days to Maturity')
            plt.ylabel('Swap Rate (%)')
            plt.legend()
            plt.show()
                
    @staticmethod
    def _interpolate_rates(day_terms, rates, interp_terms, method):
        
        func = interp1d(day_terms, rates, kind=method)
        interp_rates = [func(day) for day in interp_terms]
        
        return interp_rates
    
    @staticmethod
    def _days_in_term(term, rules):
    
        rule= {'D':
                    {'business_days':1, 'calendar_days':1},
                 'W':
                    {'business_days':5, 'calendar_days':7},
                 'M':
                    {'business_days':22, 'calendar_days':30},
                 'Y':
                     {'business_days': 252, 'calendar_days': 360}
    
                 }
    
        term_time = term[-1]
        multiplication = int(term[0:-1])
    
        maturity = rule[term_time][rules]
    
        term_days = maturity * multiplication
    
        return term_days
    