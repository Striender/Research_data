import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator

# AI/ML Workloads (26 items)
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
    "stable-diffusion.cpp.1",
    "stable-diffusion.cpp.2",
    "stable-diffusion.cpp-v1-5.2",
    "stable-diffusion.cpp-v2.1",
    "stable-diffusion.cpp-v2.2",
    "stable-diffusion.cpp-v2.3",
    "vit.cpp-base-ggml-model.1",
    "vit.cpp-large-ggml-model.1",
    "whisper_trace_1",
    "whisper_trace_2",
    "whisper_trace_3"
]

# L1d Coverage data (26 workloads, already ordered)
data_1 = [
    80.7726,
81.3327,
74.6725,
49.8813,
95.861,
94.3699,
96.3782,
97.1322,
96.2946,
97.6194,
96.9638,
97.4985,
96.791,
97.0315,
97.6519,
85.9084,
91.818,
73.2734,
48.3216,
46.3614,
92.1806,
94.6391,
89.86,
51.8776,
89.3979,
48.0576

]

data_2 = [
    84.5987,
83.5011,
79.7068,
63.9543,
94.6957,
93.2989,
95.0075,
95.4174,
95.6651,
95.6943,
95.5776,
95.8811,
95.5497,
95.898,
95.9782,
84.404,
92.6118,
80.0311,
51.2044,
64.8901,
93.4903,
93.2531,
89.7808,
59.2231,
90.3529,
54.1711

]

data_3 = [83.7284,
82.215,
79.7483,
74.349,
91.2167,
90.5179,
91.7668,
91.5447,
93.4348,
91.6354,
92.6283,
92.4142,
92.6353,
93.1476,
92.4861,
76.6332,
90.3174,
78.6015,
52.0831,
73.2167,
91.9995,
87.887,
85.1485,
69.3822,
86.2999,
64.6384

]

data_4 = [
    88.41,
77.3424,
77.9034,
80.6528,
85.0499,
85.388,
86.5068,
84.6238,
89.1766,
85.5735,
87.4043,
86.707,
87.4571,
87.9317,
86.58,
72.6162,
84.1517,
76.7535,
55.4099,
76.2102,
87.534,
79.6535,
79.3006,
73.3619,
78.1656,
71.3617

]

# Calculate averages
avg_1  = np.mean(data_1)
avg_2 = np.mean(data_2)
avg_3 = np.mean(data_3)
avg_4 = np.mean(data_4)

# Append average
plot_workloads = workloads + ["Average"]
plot_8k  = data_1  + [avg_1]
plot_16k = data_2 + [avg_2]
plot_32k = data_3 + [avg_3]
plot_64k = data_4 + [avg_4]

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
    #'font.serif': ['Times', 'Times New Roman', 'Liberation Serif'],
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

# Grouped bar setup — 4 bars, slightly narrower width
n = len(plot_workloads)
x = np.arange(n)
bar_width = 0.20

fig, ax = plt.subplots()

# Colors from palette (light → dark)
color_8k  = '#C5D3E8'
color_16k = '#8C9EBC'
color_32k = '#52688F'
color_64k = '#262f40'

ax.bar(x - 1.5*bar_width, plot_8k,  bar_width, label='8KB',  color=color_8k,  edgecolor='black', linewidth=0.5)
ax.bar(x - 0.5*bar_width, plot_16k, bar_width, label='16KB', color=color_16k, edgecolor='black', linewidth=0.5)
ax.bar(x + 0.5*bar_width, plot_32k, bar_width, label='32KB', color=color_32k, edgecolor='black', linewidth=0.5)
ax.bar(x + 1.5*bar_width, plot_64k, bar_width, label='64KB', color=color_64k, edgecolor='black', linewidth=0.5)

# Axis labels
ax.set_ylabel('L2C Accuracy (%)')

ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=45, ha='right')

# Y-axis limits and ticks
ax.set_xlim(-1.0, n)
ax.set_ylim(0, 100)
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.yaxis.set_minor_locator(MultipleLocator(5))
ax.tick_params(which='minor', length=2, color='black')

# Legend
ax.legend(
    loc='lower center',
    bbox_to_anchor=(0.5, 1.02),
    ncol=4,
    title='Region size',
    title_fontsize=4.0 * scale,
    frameon=True,
    facecolor='white',
    edgecolor='black',
    framealpha=1.0,
    fancybox=False
)

sample_dir = "../plots/"
os.makedirs(sample_dir, exist_ok=True)

out_name = 'Bingo_accuracy_region_size'
plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.pdf'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print(f"Average  8KB: {avg_1:.4f}%")
print(f"Average 16KB: {avg_2:.4f}%")
print(f"Average 32KB: {avg_3:.4f}%")
print(f"Average 64KB: {avg_4:.4f}%")