import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator

# X-axis labels (26 workloads + Geomean)
workloads = [
    "bark.cpp-bark.1",
    "bark.cpp-bark.2",
    "bark.cpp-bark.4",
    "bark.cpp-bark.5",
    "clip_trace_1",
    "clip_trace_3",
    "llama2.c-stories15M.1",
    "llama2.c-stories15M.2",
    "llama2.c-stories15M.3",
    "llama2.c-stories42M.1",
    "llama2.c-stories42M.2",
    "llama2.c-stories42M.3",
    "llama2.c-stories110M.1",
    "llama2.c-stories110M.2",
    "llama2.c-stories110M.3",
    "stable-diffusion.1",
    "stable-diffusion.2",
    "stable-diffusion.v1-5",
    "stable-diffusion.v2-1_768.1",
    "stable-diffusion.v2-1_768.2",
    "stable-diffusion.v2-1_768.3",
    "vit.cpp-base-f16",
    "vit.cpp-large-f16",
    "whisper_trace_1",
    "whisper_trace_2",
    "whisper_trace_3",
    "Geomean"
]

# Normalized IPC data (26 workloads + geomean as last entry)
data_l1d = [
    1.037503411, 1.028303356, 1.017246011, 1.056677143,
    1.000077108, 1.002683688, 1.263241279, 0.825623476,
    2.299527842, 0.626644817, 1.307134797, 0.534084548,
    1.430482324, 0.987478252, 0.938328052, 1.000181544,
    1.000101726, 1.027663967, 1.049927005, 1.008978718,
    1.000066899, 0.999707255, 1.034494911, 1.011471945,
    1.000505775, 1.009498585,
    1.023730326   # Geomean
]

data_l2 = [
    1.06243078,  1.049715798, 1.042267087, 1.131266488,
    0.999987563, 1.00409576,  1.262871467, 0.825544804,
    2.299848245, 0.626621355, 1.306913045, 0.534080208,
    1.429796214, 0.987507028, 0.938080537, 1.00023544,
    0.999791194, 1.026531747, 1.045001129, 1.03649576,
    0.999694939, 1.000216945, 1.037842385, 1.05575538,
    1.00005867,  1.057595417,
    1.033627692   # Geomean
]

data_l1_l2 = [
    1.052174122, 1.038046017, 1.032293819, 1.096154488,
    1.000077108, 1.004547222, 1.263228672, 0.825630417,
    2.300448274, 0.626662865, 1.307230235, 0.534097566,
    1.430678356, 0.987566792, 0.938390611, 1.000260969,
    1.000096372, 1.031951319, 1.072959937, 1.030427181,
    1.000061547, 1.000112393, 1.035827136, 1.046439815,
    1.000517914, 1.04866623,
    1.031565451   # Geomean
]

# Figure parameters — exact Thesis.ipynb style
scale = 1.5
fig_width_pt = 240.94499
inches_per_pt = 1.0 / 72.27
golden_mean = 0.6
fig_width = fig_width_pt * inches_per_pt * scale

params = {
    'figure.dpi': 300,
    'backend': 'ps',
    'axes.labelsize': 5.0 * scale,
    'font.size': 5.0 * scale,
    'legend.fontsize': 4.0 * scale,
    'xtick.labelsize': 4.0 * scale,
    'ytick.labelsize': 4.0 * scale,
    'text.usetex': False,
    'font.family': 'serif',
    'font.serif': ['Times', 'Times New Roman', 'Liberation Serif'],
    'patch.linewidth': 0.5,
    'patch.edgecolor': 'black',
    'figure.figsize': [fig_width, fig_width * golden_mean * 0.95],
    'figure.autolayout': True,
    'hatch.linewidth': 0.5,
    'hatch.color': 'black',
    'axes.grid': True,
    'axes.axisbelow': True,
    'axes.grid.axis': 'y',
    'grid.linestyle': '--',
    'grid.linewidth': 0.75,
    'grid.alpha': 0.3,
    'grid.color': 'black',
}
plt.rcParams.update(params)

# Grouped bar setup — 3 bars per group
n = len(workloads)
x = np.arange(n)
bar_width = 0.27

# Colors: L1D, L2, L1+L2
color_l1d    = '#8C9EBC'
color_l2     = '#52688F'
color_l1_l2  = '#262f40'

fig, ax = plt.subplots()

ax.bar(x - bar_width, data_l1d,   bar_width, label='L1D',    color=color_l1d,   edgecolor='black', linewidth=0.5)
ax.bar(x,             data_l2,    bar_width, label='L2',     color=color_l2,    edgecolor='black', linewidth=0.5)
ax.bar(x + bar_width, data_l1_l2, bar_width, label='L1+L2', color=color_l1_l2, edgecolor='black', linewidth=0.5)

# Baseline reference line at y = 1.0
ax.axhline(y=1.0, color='black', linewidth=0.75, linestyle='-', zorder=5)

# Separator line before Geomean (last bar group)
ax.axvline(x=n - 1 - 0.5, color='black', linewidth=0.5, linestyle='--', alpha=0.5)

ax.set_ylabel('Normalized IPC over baseline')
ax.set_xticks(x)
ax.set_xticklabels(workloads, rotation=45, ha='right')

# Y-axis range: fit data with some padding
ax.set_xlim(-1.0, n)
ax.set_ylim(0.4, 2.5)
ax.yaxis.set_major_locator(MultipleLocator(0.5))
ax.yaxis.set_minor_locator(MultipleLocator(0.1))
ax.tick_params(which='minor', length=2, color='black')

ax.legend(
    loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=3,
    frameon=True, facecolor='white', edgecolor='black',
    framealpha=1.0, fancybox=False
)

sample_dir = "../plots/bingo"
os.makedirs(sample_dir, exist_ok=True)

out_name = 'normalized_ipc_speedup'
plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.pdf'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print(f"Geomean — L1D: {data_l1d[-1]:.4f}  L2: {data_l2[-1]:.4f}  L1+L2: {data_l1_l2[-1]:.4f}")