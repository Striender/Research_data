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

# Reduction in Miss Latency data (26 workloads, already ordered)
data_l1d = [
     66.73680803,
34.15204678,
36.35386819,
62.83520641,
72.68550034,
73.15730196,
87.06981318,
87.00846192,
85.03130336,
86.6479221,
86.26158599,
88.51198242,
86.48317209,
87.82780465,
86.92517007,
32.39312472,
33.63557858,
19.1198786,
15.95698925,
31.19037744,
33.40563991,
34.6184739,
55.30139935,
56.5681961,
71.81615065,
56.53673163
]

data_l2 = [
     12.22997674,
-20.78077425,
-11.35204082,
35.93974175,
-3.68914909,
-37.07785052,
14.73922902,
3.827675829,
2.402899236,
6.697724148,
4.335193822,
10.33481119,
3.414264036,
6.075546117,
2.718873069,
0.892857143,
11.68556311,
-54.77764813,
-0.516562807,
32.18906589,
12.91993601,
-41.25887187,
7.806162385,
37.53108088,
6.318980258,
38.87454827
]

data_llc = [
    -33.59753045,
-33.44925016,
-30.35890033,
-59.03208651,
-30.00298835,
-109.5896554,
-21.08399221,
-12.43199444,
-9.541454377,
-5.515973339,
-6.16375345,
-23.78713155,
-8.358381503,
-17.09628945,
-10.52510098,
-43.61408544,
-32.02436637,
-30.21293692,
-41.65196472,
-35.28347407,
-31.31000993,
-29.38415473,
-1.882315723,
-23.78100219,
-27.85231794,
-16.99024937
]

# Calculate averages
avg_l1d = np.mean(data_l1d)
avg_l2  = np.mean(data_l2)
avg_llc = np.mean(data_llc)

plot_workloads = workloads + ["Average"]
plot_l1d = data_l1d + [avg_l1d]
plot_l2  = data_l2  + [avg_l2]
plot_llc = data_llc + [avg_llc]

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
   # 'font.serif': ['Times', 'Times New Roman', 'Liberation Serif'],
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

# Grouped bar setup — 3 bars
n = len(plot_workloads)
x = np.arange(n)
bar_width = 0.27

fig, ax = plt.subplots()

color_l1d = '#8C9EBC'
color_l2  = '#52688F'
color_llc = '#262f40'

ax.bar(x - bar_width, plot_l1d, bar_width, label='L1d', color=color_l1d, edgecolor='black', linewidth=0.5)
ax.bar(x,             plot_l2,  bar_width, label='L2',  color=color_l2,  edgecolor='black', linewidth=0.5)
ax.bar(x + bar_width, plot_llc, bar_width, label='LLC', color=color_llc, edgecolor='black', linewidth=0.5)

# Zero baseline — solid prominent line
ax.axhline(y=0, color='black', linewidth=0.75, linestyle='-', zorder=5)

ax.set_ylabel('Reduction in Miss latency (%)')
ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=45, ha='right')
ax.set_xlim(-1.0, n)

# Symmetric-ish y range: max = 100, min = -100 (mirrors y_max)
ax.set_ylim(-100, 100)
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.yaxis.set_minor_locator(MultipleLocator(10))
ax.tick_params(which='minor', length=2, color='black')

ax.legend(
    loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=3,
    frameon=True, facecolor='white', edgecolor='black',
    framealpha=1.0, fancybox=False
)

sample_dir = "../plots/bingo/Miss_latency/"
os.makedirs(sample_dir, exist_ok=True)

out_name = 'Bingo_reduction_in_miss_latency'
plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.pdf'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print(f"Average L1d: {avg_l1d:.4f}%")
print(f"Average L2:  {avg_l2:.4f}%")
print(f"Average LLC: {avg_llc:.4f}%")
