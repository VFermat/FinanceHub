"""
Authors: Vitor Eller (@Vfermat) and Liam Dunphy (@ldunphy98)
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

from scipy.interpolate import interp1d
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
from Interpolation.FlatForward import FlatForward


class SwapCurve(object):

    interpolate_display = {
            'linear': 'r-',
            'cubic': 'g--',
            'quadratic': 'b:',
            'nearest': 'y-.',
            'flatforward': 'r-'
            }

    conventions = {
            'business_days': 252,
            'calendar_days': 360
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
        self.convention_year = self.conventions[convention]
        self.rates = rates

    def plot_3d(self, plot_type='surface'):

        x = self.rates.index
        y = self.rates.columns
        # Creating 2D Array with swap rates
        z = []
        for column in y:
            base_curve = self.rates[column]
            curve = self._get_3d_curve(base_curve, x)
            z.append(curve)
        z = np.array(z)
        # Converting x (maturities terms) to days to maturities
        x = [self._days_in_term(term, self.convention) for term in x]
        # Converting y (dates) to number. Otherwise, plot will not work
        inty = [0]
        for date in y:
            if date != y[0]:
                diff = date - y[0]
                inty.append(diff.days)
        y = inty
        # Creating 2D arrays for x and y
        x, y = np.meshgrid(x, y)

        # Plotting Graphic
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        if plot_type == 'surface':
            ax.plot_surface(y, x, z)
        elif plot_type == 'wireframe':
            ax.plot_wireframe(y, x, z)
        else:
            raise ValueError('Invalid Plot Type. Please read documentation for valid plots.')
        ax.set_xlabel('Date')
        ax.set_ylabel('Days to Maturity')
        ax.set_zlabel('Swap Rate (%)')

    def get_rate(self, base_curves, desired_terms,
                 interpolate_methods=['cubic']):
        """
        Function that get the Swap Rate for a specific term. It calculates
        based on the interpolation of the base curve.

        Parameters
        ----------
        base_curves : array_like
            Curves that will be used on the interpolation, to discover the
            rate for a specific term.
        desired_terms : array_like
            Terms you want to find the swap rate. Should be passed as days.
            (future development will allow you to input a desired date.)
        interpolate_methods : array_like, optional
            Methods used to interpolate the curve. Only works if `interpolate`
            is True. Default is 'cubic'.

            Accepted methods are: `linear`, `cubic`, `quadratic`,
            and `nearest`.

        Returns
        ----------
        info : dict
            A dictionary containing the rates for the asked terms. If more than
            one base curve is used, there will be one rate for each term, for
            each base curve.

            The dictionary has two `levels`, being as follow:
                info = {'interpolate_method': {'term': 'rate'}}
        """

        # Checking inputs
        if type(base_curves) not in (list, np.ndarray):
            raise TypeError("Argument 'base_curves' should be array_like.")
        if type(desired_terms) not in (list, np.ndarray):
            raise TypeError("Argument 'desired_terms' should be array_like.")
        if type(interpolate_methods) not in (list, np.ndarray):
            raise TypeError("Argument 'interpolate_methods' should be array_like.")

        # Checking if base_curves are valid:
        curves = []
        for date in base_curves:
            try:
                curve = self.rates[date]
                curve = curve.dropna()
            except IndexError as e:
                print('{}. {} is an invalid date, since there is not a curve for this date. It will not be used.'.format(e, date))
            else:
                curves.append(curve)

        # Checking if there are curves to be plotted
        if len(curves) == 0:
            raise ValueError('There are no Base Curves to be used.')

        # Creating dataFrame with information asked
        info = {}
        for method in interpolate_methods:
            info[method] = pd.DataFrame()
        for curve in curves:
            for method in interpolate_methods:
                terms = curve.index
                dterms = [self._days_in_term(t, self.convention) for
                        t in terms]
                n_desired_terms = desired_terms.copy()
                # Checks if desired_terms are valid
                for term in desired_terms:
                    if term < min(dterms) or term > max(dterms):
                        print('{} is an invalid term.'.format(term))
                        n_desired_terms.remove(term)
                irates = self._interpolate_rates(dterms, list(curve),
                                                n_desired_terms, method,
                                                self.convention_year)
                rates = {k: v for k, v in zip(n_desired_terms,
                                            irates)}
                for k in rates.keys():
                    info[method].at[curve.name, k] = rates[k]

        return info

    def get_forward_historic(self, maturity1, maturity2, plot=False,
                            interpolate_method='cubic'):

        historic = pd.Series()
        for i in range(len(self.rates.columns)):
            date = self.rates.columns[i]
            rate1 = self.get_rate([date], [maturity1],
                                  [interpolate_method])[interpolate_method][maturity1][date]
            rate2 = self.get_rate([date], [maturity2],
                                  [interpolate_method])[interpolate_method][maturity2][date]
            forward = self._forward_rate(date, maturity1, maturity2,
                                        rate1, rate2, self.convention_year)
            historic.at[date] = forward
        if plot:
            historic.plot()
            plt.show()

        return historic

    def plot_historic_rates(self, maturity):
        terms = self.rates.index
        day_terms = [self._days_in_terms(term, self.convention) for term in terms]
        if maturity in day_terms:
            historic_rates_curve = self.rates.loc[maturity]
            historic_rates_curve.plot()
            plt.show()
        else:
            dates = self.rates.columns

            response = self.get_rate(dates, maturity)
            table_term = response["cubic"][maturity]

            table_term.plot()

    def plot_day_curve(self, dates, interpolate=False,
                       interpolate_methods=['cubic'], scatter=False):
        """
        Function to plot the SwapCurve for a specific set of days.

        Parameters
        ----------
        dates : array_like
            Dates to be plotted.

            Obs: A great improvement would be to allow the user to pick a date
            that we do not have the curve, and plot it. So basically construct
            the curve for a specific day, based on near ones.
        interpolate : boolean, optional
            If you want to create and interpolation of the curve or not.
            If interpolate is False, curve plotted will be similar to a
            `linear` interpolation. Default is False.
        interpolate_methods : array_like, optional
            Methods used to interpolate the curve. Only works if `interpolate`
            is True. Default is 'cubic'.

            Accepted methods are: `linear`, `cubic`, `quadratic`,
            and `nearest`.
        scatter : boolean, optional
            Only works if `interpolate` is False. If `scatter` is True, then
            instead of plotting something close to a `linear` interpolation,
            the graphic will look like a scatter plot.

        See Also
        ----------
        plot_term_historic : plot the historic rate for the desired term
        """
        # Checking Inputs
        if type(dates) not in (list, np.ndarray):
            raise TypeError("Argument 'dates' should be array_like.")
        if type(interpolate_methods) not in (list, np.ndarray) and interpolate_methods is not None:
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
            date = date.strftime('%d/%b/%Y')
            if interpolate:
                if len(interpolate_methods) == 1:
                    terms = curve.index
                    dterms = [self._days_in_term(t, self.convention) for
                              t in terms]
                    iterms = np.arange(min(dterms), max(dterms), 10)
                    irates = self._interpolate_rates(dterms, list(curve),
                                                     iterms,
                                                     interpolate_methods[0],
                                                     self.convention_year)
                    plt.plot(iterms, irates, label=date)
                    plt.legend()
                    plt.xlabel('Days to Maturity')
                    plt.ylabel('Swap Rate (%)')
                else:
                    """
                    If there are more than one interpolation method to be used
                    ther will be created an specific graphic for each desired
                    date (if there are more than one). This happens to
                    ensure visualization of the data.
                    """
                    terms = curve.index
                    dterms = [self._days_in_term(t, self.convention) for
                              t in terms]
                    iterms = np.arange(min(dterms), max(dterms), 10)
                    for method in interpolate_methods:
                        plot_type = self.interpolate_display[method]
                        irates = self._interpolate_rates(dterms, list(curve),
                                                         iterms, method,
                                                         self.convention_year)
                        plt.plot(iterms, irates, plot_type, label=method)
                    plt.xlabel('Days to Maturity')
                    plt.ylabel('Swap Rate (%)')
                    plt.title(date)
                    plt.legend()
                    plt.show()
                    plotted = True
            else:
                if not scatter:
                    curve.plot(label=date)
                else:
                    terms = curve.index
                    dterms = [self._days_in_term(t, self.convention) for
                              t in terms]
                    rates = curve.tolist()
                    plt.plot(dterms, rates, 'o', label=date)

        if not plotted:
            plt.xlabel('Days to Maturity')
            plt.ylabel('Swap Rate (%)')
            plt.legend()
            plt.show()

    def _get_3d_curve(self, base_curve, maturities):

        icurve = base_curve.copy()
        icurve = icurve.dropna()

        icurve_maturities = icurve.index
        icurve_dmaturities = [self._days_in_term(term, self.convention) for
                              term in icurve_maturities]
        max_maturity = max(icurve_dmaturities)
        min_maturity = max(icurve_dmaturities)
        date = base_curve.name

        for maturity in maturities:
            dmaturity = self._days_in_term(maturity, self.convention)
            if (dmaturity > min_maturity and dmaturity < max_maturity) and dmaturity not in icurve_dmaturities:
                rate = self.get_rate(date, dmaturity)['cubic'][dmaturity]
                base_curve[maturity] = rate

        return base_curve

    @staticmethod
    def _interpolate_rates(day_terms, rates, interp_terms,
                           method, convention_days):

        if method != 'flatforward':
            func = interp1d(day_terms, rates, kind=method)
            interp_rates = [func(day) for day in interp_terms]
        else:
            ff = FlatForward()
            interp_rates = ff.interpolate(rates, day_terms,
                                          interp_terms, convention_days)

        return interp_rates

    @staticmethod
    def _days_in_term(term, rules):

        rule = {
                'D':
                    {'business_days': 1, 'calendar_days': 1},
                'W':
                    {'business_days': 5, 'calendar_days': 7},
                'M':
                    {'business_days': 22, 'calendar_days': 30},
                'Y':
                    {'business_days': 252, 'calendar_days': 360}
            }

        term_time = term[-1]
        multiplication = int(term[0:-1])

        maturity = rule[term_time][rules]

        term_days = maturity * multiplication

        return term_days

    @staticmethod
    def _forward_rate(base_date, maturity1, maturity2, rate1, rate2, convention):

        maturity1_date = base_date + dt.timedelta(days=maturity1)
        maturity2_date = base_date + dt.timedelta(days=maturity2)

        business_days1 = np.busday_count(base_date, maturity1_date)
        business_days2 = np.busday_count(base_date, maturity2_date)

        days_to_years1 = (business_days1/convention)
        days_to_years2 = (business_days2/convention)

        numerator = (1+rate1)**days_to_years2
        denominator = (1+rate2)**days_to_years1

        get_forward = ((numerator/denominator)-1)*100

        return get_forward