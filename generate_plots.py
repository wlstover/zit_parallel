import argparse
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import ScalarFormatter

parser = argparse.ArgumentParser(description='Generate ZIT parallel speedup plots')
parser.add_argument('--python', required=True, help='Path to Python trading log CSV')
parser.add_argument('--cython', required=True, help='Path to Cython trading log CSV')
args = parser.parse_args()

python_df = pd.read_csv(args.python)
cython_df = pd.read_csv(args.cython)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def prepare_df(df):
    average_df = df.groupby(['Threads', 'Buyers', 'Sellers']).mean().reset_index()
    average_df.sort_values(['NumberOfTrades', 'Threads'], ascending=True, inplace=True)
    average_df['Speedup'] = average_df.groupby('NumberOfTrades')['WallTime'].transform(lambda x: x.iloc[0] / x)
    return average_df

python_avg = prepare_df(python_df)
cython_avg = prepare_df(cython_df)

line_styles = {20000: ':', 200000: '--', 2000000: '-'}

for avg_df, filename in [(python_avg, f'zit_parallel_python_{timestamp}.png'),
                          (cython_avg, f'zit_parallel_cython_{timestamp}.png')]:
    fig, ax = plt.subplots(figsize=(8, 5))

    for number_of_trades, group in avg_df.groupby('NumberOfTrades'):
        ax.plot(group['Threads'], group['Speedup'], line_styles[number_of_trades],
                color='black', linewidth=0.9)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1, 500)

    # X-axis ticks to match paper style
    ax.set_xticks([1, 5, 10, 50, 100, 500])
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    ax.tick_params(axis='x', which='minor', bottom=False)

    # Y-axis: clean scalar ticks, no scientific notation
    ax.get_yaxis().set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(ScalarFormatter())

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Axis labels at the ends, matching paper style
    ax.annotate('Threads', xy=(1, 0), xytext=(5, -mpl.rcParams['xtick.major.pad'] + 10),
                ha='left', va='top', xycoords='axes fraction', textcoords='offset points', fontsize=11)
    ax.annotate('Speedup', xy=(0, 1), xytext=(-mpl.rcParams['xtick.major.pad'] + 25, 10),
                ha='right', va='bottom', xycoords='axes fraction', textcoords='offset points', fontsize=11)

    # Remove default axis labels
    ax.set_xlabel('')
    ax.set_ylabel('')

    plt.tight_layout()
    plt.savefig(f'outputs/figures/{filename}', dpi=150)
    print(f'Saved outputs/figures/{filename}')

print('Done')
