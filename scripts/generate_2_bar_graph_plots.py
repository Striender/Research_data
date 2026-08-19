import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator

# AI/ML Workloads — final order: 15M → 42M → 110M
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
# 2KB data
data_baseline = [
2.3027350   ,
3.0984050,
4.0691700,
21.6387150,
3.1072800,
3.9226300,
32.8462700,
31.9665650,
31.1297900,
34.4156750,
34.0699600,
34.9652450,
35.1379200,
35.4804700,
35.1219100,
8.7065000,
7.2635650,
3.4719550,
6.3610750,
7.2287450,
7.3043200,
2.5980300,
3.2973600,
5.0791550,
5.4460400,
5.2286400
]


data_prefetcher =  [
1.21947,
1.93870,
2.40717,
0.00000,
0.24732,
0.27466,
0.00000,
0.00000,
0.00434,
0.00000,
0.00000,
0.04287,
0.13963,
0.00000,
0.02968,
0.89181,
0.14812,
2.13971,
4.91059,
0.00000,
0.39273,
2.14933,
2.21663,
0.00000,
0.00000,
0.00000
]

# Calculate averages
avg_baseline   = np.mean(data_baseline)
avg_prefetcher = np.mean(data_prefetcher)

plot_workloads    = workloads + ["Average"]
plot_baseline     = data_baseline   + [avg_baseline]
plot_prefetcher   = data_prefetcher + [avg_prefetcher]

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

# Grouped bar setup — 2 bars
n = len(plot_workloads)
x = np.arange(n)
bar_width = 0.27

fig, ax = plt.subplots()

color_baseline   = '#8C9EBC'
color_prefetcher = '#394761'

ax.bar(x - bar_width/2, plot_baseline,   bar_width, label='Prefetch Issued',   color=color_baseline,   edgecolor='black', linewidth=0.5)
ax.bar(x + bar_width/2, plot_prefetcher, bar_width, label='Prefetch Filled', color=color_prefetcher, edgecolor='black', linewidth=0.5)

ax.set_ylabel('Coverage (%)')
ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=45, ha='right')
ax.set_xlim(-1.0, n)

# Y-axis: auto-range with 20-unit major ticks
y_max = max(max(plot_baseline), max(plot_prefetcher))
ax.set_ylim(0,100)
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.yaxis.set_minor_locator(MultipleLocator(5))
ax.tick_params(which='minor', length=2, color='black')

ax.legend(
    loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=2,
    frameon=True, facecolor='white', edgecolor='black',
    framealpha=1.0, fancybox=False
)

out_name = "Bingo_l2_Coverage_plot"
root_dir = "../plots/Pref/Coverage"
os.makedirs(root_dir, exist_ok=True)

out_png = os.path.join(root_dir, f'{out_name}.png')
out_pdf = os.path.join(root_dir, f'{out_name}.pdf')

plt.savefig(out_png, bbox_inches='tight')
plt.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print(f"Average Baseline:   {avg_baseline:.4f}")
print(f"Average Prefetcher: {avg_prefetcher:.4f}")
print(os.path.abspath("../plots/Pref/Coverage"))