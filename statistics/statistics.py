import os, os.path
import pandas as pd
import matplotlib
try:
    matplotlib.use('TkAgg')
except:
    pass
import matplotlib.pyplot as plt
import seaborn as sns
from qstrader import settings

class Statistics():
    def create_drawdowns(self, pnl):
        """
        Calculate the largest peak-to-trough drawdown of the PnL curve
        as well as the duration of the drawdown. Requires that the 
        pnl_returns is a pandas Series.
        Parameters:
        pnl - A pandas Series representing period percentage returns.
        Returns:
        drawdown, duration - Highest peak-to-trough drawdown and duration.
        """

        # Calculate the cumulative returns curve 
        # and set up the High Water Mark
        hwm = [0]

        # Create the drawdown and duration series
        idx = pnl.index
        drawdown = pd.Series(index = idx)
        duration = pd.Series(index = idx)

        # Loop over the index range
        for t in range(1, len(idx)):
            hwm.append(max(hwm[t-1], pnl.ix[t]))
            drawdown.ix[t]= (hwm[t]-pnl.ix[t])
            duration.ix[t]= (0 if drawdown.ix[t] == 0 else duration.ix[t-1]+1)
        return drawdown, drawdown.max(), duration.max()


    def generate_results(self):
        in_filename = "equity.csv"
        out_filename = "output.csv" 
        in_file = os.path.join(settings.OUTPUT_DIR, in_filename)
        out_file = os.path.join(settings.OUTPUT_DIR, out_filename)

        # Create equity curve dataframe
        df = pd.read_csv(in_file, index_col=0)
        df.dropna(inplace=True)
        df["Total"] = df.sum(axis=1)
        df["Returns"] = df["Total"].pct_change()
        df["Equity"] = (1.0+df["Returns"]).cumprod()
        
        # Create drawdown statistics
        drawdown, max_dd, dd_duration = self.create_drawdowns(df["Equity"])
        df["Drawdown"] = drawdown

        df.to_csv(out_file, index=True)
        
        print("Simulation complete and results exported to %s" % out_filename)


    def plot_results(self):
        """
        A simple script to plot the balance of the portfolio, or
        "equity curve", as a function of time.
        It requires OUTPUT_RESULTS_DIR to be set in the project
        settings.
        """
        sns.set_palette("deep", desat=.6)
        sns.set_context(rc={"figure.figsize": (8, 4)})

        equity_file = os.path.join(settings.OUTPUT_DIR, "output.csv")
        equity = pd.io.parsers.read_csv(
            equity_file, parse_dates=True, header=0, index_col=0
        )

        # Plot three charts: Equity curve, period returns, drawdowns
        fig = plt.figure()
        fig.patch.set_facecolor('white')     # Set the outer colour to white
        
        # Plot the equity curve
        ax1 = fig.add_subplot(311, ylabel='Portfolio value')
        equity["Equity"].plot(ax=ax1, color=sns.color_palette()[0])

        # Plot the returns
        ax2 = fig.add_subplot(312, ylabel='Period returns')
        equity['Returns'].plot(ax=ax2, color=sns.color_palette()[1])

        # Plot the returns
        ax3 = fig.add_subplot(313, ylabel='Drawdowns')
        equity['Drawdown'].plot(ax=ax3, color=sns.color_palette()[2])

        # Plot the figure
        plt.show()