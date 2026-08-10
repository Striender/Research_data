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
    "whisper_trace_3"
]

# 1KB data
data_1kb = [
    7.8961,
18.7641,
16.8521,
6.0145,
21.5152,
18.9274,
3.9285,
6.9288,
2.7791,
6.9237,
4.7444,
6.5261,
4.1577,
4.8528,
6.9202,
6.7537,
5.7140,
31.2444,
64.8096,
30.2283,
5.6862,
4.7244,
4.4498,
13.2897,
15.2618,
16.1582


]

# 2KB data
data_2kb = [
    13.5839,
43.3167,
39.4093,
5.9174,
22.6923,
17.1253,
0.2323,
0.3170,
0.6751,
0.0075,
0.0169,
0.1580,
0.0131,
0.0101,
0.0027,
10.0993,
4.4984,
25.8127,
66.3175,
21.2764,
4.4493,
60.7518,
22.1424,
17.4371,
16.8316,
18.7614


]

# 4KB data
data_4kb = [
   21.2786,
48.0674,
43.0959,
5.2702,
21.5439,
18.1724,
0.1582,
0.3468,
0.5504,
0.0049,
0.0178,
0.1410,
0.0118,
0.0108,
0.0049,
8.5852,
96.1166,
28.3833,
68.0211,
19.1362,
96.6325,
61.6305,
43.3164,
31.5081,
20.6580,
28.9173


]

# Validate that every dataset matches the workload count
assert len(data_1kb) == len(workloads)
assert len(data_2kb) == len(workloads)
assert len(data_4kb) == len(workloads)

# Calculate averages
avg_1kb = np.mean(data_1kb)
avg_2kb = np.mean(data_2kb)
avg_4kb = np.mean(data_4kb)

# Append average
plot_workloads = workloads + ["Average"]
plot_1kb = data_1kb + [avg_1kb]
plot_2kb = data_2kb + [avg_2kb]
plot_4kb = data_4kb + [avg_4kb]

# Figure parameters
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

# Grouped bar setup
n = len(plot_workloads)
x = np.arange(n)

# Smaller width to accommodate three bars
bar_width = 0.27

fig, ax = plt.subplots()

# Colors
color_1kb = '#8C9EBC'
color_2kb = '#394761'
color_4kb = '#B5BFCF'

# Three bars centered around each workload position
bars1 = ax.bar(
    x - bar_width,
    plot_1kb,
    bar_width,
    label='1KB',
    color=color_1kb,
    edgecolor='black',
    linewidth=0.5
)

bars2 = ax.bar(
    x,
    plot_2kb,
    bar_width,
    label='2KB',
    color=color_2kb,
    edgecolor='black',
    linewidth=0.5
)

bars3 = ax.bar(
    x + bar_width,
    plot_4kb,
    bar_width,
    label='4KB',
    color=color_4kb,
    edgecolor='black',
    linewidth=0.5
)

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
    ncol=3,
    title='Region size',
    title_fontsize=4.0 * scale,
    frameon=True,
    facecolor='white',
    edgecolor='black',
    framealpha=1.0,
    fancybox=False
)

root_dir = "../plots/"
os.makedirs(root_dir, exist_ok=True)

out_png = os.path.join(root_dir, 'Gaze_l2_prefetcher_accuracy.png')
out_pdf = os.path.join(root_dir, 'Gaze_l2_prefetcher_accuracy.pdf')

plt.savefig(out_png, bbox_inches='tight')
plt.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Saved: {out_png}")
print(f"Saved: {out_pdf}")
print(f"Average 1KB: {avg_1kb:.4f}%")
print(f"Average 2KB: {avg_2kb:.4f}%")
print(f"Average 4KB: {avg_4kb:.4f}%")
