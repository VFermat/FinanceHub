"""
@author: Vitor Eller - @VFermat
"""

import pandas as pd
import numpy as np
from pandas.tseries.offsets import MonthEnd

class HXLFactors(object):
    
    high_ROE = ['BHIAHR', 'BMIAHR', 'BLIAHR', 'SHIAHR', 'SMIAHR', 'SLIAHR']
    low_ROE = ['BHIALR', 'BMIALR', 'BLIALR', 'SHIALR', 'SMIALR', 'SLIALR']
    high_IA = ['BHIAHR', 'BHIAMR', 'BHIALR', 'SHIAHR', 'SHIAMR', 'SHIALR']
    low_IA = ['BLIAHR', 'BLIAMR', 'BLIALR', 'SLIAHR', 'SLIAMR', 'SLIALR']
    
    
    def calculate_factors(self, prices, dividends, assets, ROE, marketcap):
        
        # Lining up dates to end of month
        prices.columns = prices.columns + MonthEnd(0)
        dividends.columns = dividends.columns + MonthEnd(0)
        assets.columns = assets.columns + MonthEnd(0)
        ROE.columns = ROE.columns + MonthEnd(0)
        marketcap.columns = marketcap.columns + MonthEnd(0)
        
        # Padronizing columns
        dividends, assets, ROE = self._padronize_columns(prices.columns, 
                                                         dividends,
                                                         assets,
                                                         ROE)
        
        # Basic information
        self.securities = {
                'assets': assets,
                'ROE': ROE,
                'price': prices,
                'marketcap': marketcap,
                'dividends': dividends
                }
        
        # Gathering info
        self.securities = self._get_IA_info(self.securities)
        self.securities = self._get_return(self.securities)
        self.securities = self._get_benchmarks(self.securities)
        self.securities['sizecls'] = self._get_sizecls(self.securities)
        self.securities['iacls'] = self._get_iacls(self.securities)
        self.securities['ROEcls'] = self._get_ROEcls(self.securities)
        self.securities['cls'] = self.securities['sizecls'] + self.securities['iacls'] + self.securities['ROEcls']
        
        # Calculating factors
        self.HXLInvestment = self.get_investment()
        self.HXLProfit = self.get_profit()
    
    def get_profit(self):
        
        lreturns = self.securities['lreturn']
        stocks_cls = self.securities['cls']
        marketcap = self.securities['marketcap']
        HXLProfit = pd.Series(index=stocks_cls.columns)
        
        for c in stocks_cls.columns:
            phigh_returns = []
            plow_returns = []
            for scls in self.high_ROE:
                high_investment = stocks_cls[stocks_cls[c] == scls].index
                high_returns = lreturns.loc[high_investment, c]
                phigh_returns.append(np.sum(high_returns*marketcap.loc[high_investment, c])/np.sum(marketcap.loc[high_investment, c]))

            for scls in self.low_ROE:            
                low_investment = stocks_cls[stocks_cls[c] == scls].index
                low_returns = lreturns.loc[low_investment, c]
                plow_returns.append(np.sum(low_returns*marketcap.loc[low_investment, c])/np.sum(marketcap.loc[low_investment, c]))
            
            factor = np.mean(phigh_returns) - np.mean(plow_returns)
            
            HXLProfit.at[c] = factor
            
        return HXLProfit
    
    def get_investment(self):
        
        lreturns = self.securities['lreturn']
        stocks_cls = self.securities['cls']
        marketcap = self.securities['marketcap']
        HXLInvestment = pd.Series(index=stocks_cls.columns)
        
        for c in stocks_cls.columns:
            phigh_returns = []
            plow_returns = []
            for scls in self.high_IA:
                high_investment = stocks_cls[stocks_cls[c] == scls].index
                high_returns = lreturns.loc[high_investment, c]
                phigh_returns.append(np.sum(high_returns*marketcap.loc[high_investment, c])/np.sum(marketcap.loc[high_investment, c]))

            for scls in self.low_IA:            
                low_investment = stocks_cls[stocks_cls[c] == scls].index
                low_returns = lreturns.loc[low_investment, c]
                plow_returns.append(np.sum(low_returns*marketcap.loc[low_investment, c])/np.sum(marketcap.loc[low_investment, c]))
            
            factor = np.mean(phigh_returns) - np.mean(plow_returns)
            
            HXLInvestment.at[c] = factor
            
        return HXLInvestment
            
        
        
    @staticmethod
    def _get_ROEcls(securities):
        """
        Divides the securities in High, Medium and Low, based on the percentiles of the
        ROE (30% and 70%).
    
        Parameters
        ----------
        securities : Dict like
            A dict containing the information on stocks. 
            
        Return
        ----------
        ROEcls : DataFrame
            A DataFrame containing the stocks classification.
        """        
        
        ROEcls = pd.DataFrame(index=securities['ROE'].index, 
                             columns=securities['ROE'].columns)
        ROE30 = securities['ROE30']
        ROE70 = securities['ROE70']
        
        for c in securities['ROE'].columns:
            benchmark30 = ROE30[c]
            benchmark70 = ROE70[c]
            for i in securities['ROE'].index:
                stock_ROE = securities['ROE'].loc[i, c]
                
                if stock_ROE == np.NaN or stock_ROE == 0:
                    ROEcls.at[i, c] = np.NaN
                elif stock_ROE <= benchmark30:
                    ROEcls.at[i, c] = 'LR'
                elif stock_ROE <= benchmark70:
                    ROEcls.at[i, c] = 'MR'
                else:
                    ROEcls.at[i, c] = 'HR'
                    
        return ROEcls
    
    @staticmethod
    def _get_iacls(securities):
        """
        Divides the securities in High, Medium and Low, based on the percentiles of the
        Investment over Assets ratio (30% and 70%).
    
        Parameters
        ----------
        securities : Dict like
            A dict containing the information on stocks. 
            
        Return
        ----------
        iacls : DataFrame
            A DataFrame containing the stocks classification.
        """        
        
        iacls = pd.DataFrame(index=securities['I/A'].index, 
                             columns=securities['I/A'].columns)
        ia30 = securities['IA30']
        ia70 = securities['IA70']
        
        for c in securities['I/A'].columns:
            benchmark30 = ia30[c]
            benchmark70 = ia70[c]
            for i in securities['I/A'].index:
                stock_ia = securities['I/A'].loc[i, c]
                
                if stock_ia == np.NaN or stock_ia == 0:
                    iacls.at[i, c] = np.NaN
                elif stock_ia <= benchmark30:
                    iacls.at[i, c] = 'LIA'
                elif stock_ia <= benchmark70:
                    iacls.at[i, c] = 'MIA'
                else:
                    iacls.at[i, c] = 'HIA'
                    
        return iacls
    
    @staticmethod
    def _get_sizecls(securities):
        """
        Divides the securities in Big and Small, based on the median of the
        marketcap.
    
        Parameters
        ----------
        securities : Dict like
            A dict containing the information on stocks. 
            
        Return
        ----------
        sizecls : DataFrame
            A DataFrame containing the stocks classification.
        """        
        
        sizecls = pd.DataFrame(index=securities['marketcap'].index, 
                               columns=securities['marketcap'].columns)
        sizemedian = securities['mkmedian']
        
        for c in sizecls.columns:
            benchmark = sizemedian[c]
            for i in sizecls.index:
                stock_size = securities['marketcap'].loc[i, c]
                
                if stock_size == np.NaN or stock_size == 0:
                    sizecls.at[i, c] = np.NaN
                elif stock_size <= benchmark:
                    sizecls.at[i, c] = 'S'
                else:
                    sizecls.at[i, c] = 'B'
                    
        return sizecls
        
    
    @staticmethod        
    def _get_benchmarks(securities):
        """
        Calculates the benchmarks that will be used to sort the securities.
    
        Parameters
        ----------
        securities : Dict like
            A dict containing the information on stocks. 
            
        Return
        ----------
        n_securities : Dict
            Updated dict containing the benchmarks.
        """
        
        iaratio = securities['I/A']
        marketcap = securities['marketcap']
        ROE = securities['ROE']
        
        iapercentiles = iaratio.describe(percentiles=[0.3, 0.7]).loc[['30%', '70%']]
        ia30 = iapercentiles.loc['30%']
        ia70 = iapercentiles.loc['70%']
        
        marketcapmedian = marketcap.describe().loc['50%']
        
        ROEpercentiles = ROE.describe(percentiles=[0.3, 0.7]).loc[['30%', '70%']]
        ROE30 = ROEpercentiles.loc['30%']
        ROE70 = ROEpercentiles.loc['70%']
        
        n_securities = securities.copy()
        n_securities['IA30'] = ia30
        n_securities['IA70'] = ia70
        n_securities['mkmedian'] = marketcapmedian
        n_securities['ROE30'] = ROE30
        n_securities['ROE70'] = ROE70
        
        return n_securities
    
    @staticmethod
    def _get_return(securities):
        """
        Calculates the return for each security over time and related information.
    
        Parameters
        ----------
        securities : Dict like
            A dictionary containing the information on stocks. 
            
        Return
        ----------
        n_securities : Dict
            Updated dict containing the return for each security over time.
        """
        
        n_securities = securities.copy()
        
        n_securities['lprice'] = n_securities['price'].shift(1, axis=1)
        n_securities['pdifference'] = n_securities['price'] - n_securities['lprice']
        n_securities['gain'] = n_securities['dividends'] + n_securities['pdifference']
        n_securities['return'] = n_securities['gain']/n_securities['lprice']
        
        # Creates a return field which is shifted one month back. Will be used 
        # when calculating the factors
        n_securities['lreturn'] = n_securities['return'].shift(-1, axis=1)
        
        return n_securities
        
        
    @staticmethod
    def _get_IA_info(securities):
        """
        Calculates the Investment over Assets ratio and related information
    
        Parameters
        ----------
        securities : Dict like
            A dict containing the information on stocks. 
            
        Return
        ----------
        n_securities : Dict
            Updated dict containing Investment over Assets ratio and related information.
        """
        
        n_securities = securities.copy()
        # Calculates 1-year-lagged-assets
        n_securities['lassets'] = n_securities['assets'].shift(12, axis=1)
        # Calculates Investment
        n_securities['investment'] = n_securities['assets'] - n_securities['lassets']
        # Calculates Investment over Assets ratio
        n_securities['I/A'] = n_securities['investment']/n_securities['lassets']
        
        return n_securities
    
    @staticmethod
    def _padronize_columns(pattern, dividends, assets, ROE):
        """
        Padronizes information that is not released monthly. In that way, we do not
        encounter problems while manipulating data.
        
        Parameters
        ----------
        pattern : Array like
            Array containing the pattern for the columns
        dividends : DataFrame like
            Dataframe containing information on dividends
        assets : DataFrame like
            Dataframe containing information on assets
        ROE : DataFrame like
            Dataframe containing information on ROE
            
        Return
        ----------
        ndividends : Dataframe like
            Updated Dataframe containing information on dividends
        nassets : Dataframe like
            Updated Dataframe containing information on assets
        nROE : Dataframe like
            Updated Dataframe containing information on ROE
        """
        
        ndividends = pd.DataFrame(index=dividends.index)
        nassets = pd.DataFrame(index=assets.index)
        nROE = pd.DataFrame(index=ROE.index)
        
        for date in pattern:
            
            if date in dividends.columns:
                ndividends[date] = dividends[date]
            else:
                ndividends[date] = 0
                
            if date in assets.columns:
                nassets[date] = assets[date]
                nROE[date] = ROE[date]
            else:
                nassets[date] = 0
                nROE[date] = 0
            
        return ndividends, nassets, nROE
            
                
    
"""
TO DO:
    IA cls is rebalancing every month. Need to change it so it rebalances only at the end of June.
    Same thing is happening to Size cls.
    
    Write the description of get_profit and get_investment functions.
    Write the description of the calculate_factors function.
    Write the description of the Class.
"""
    
