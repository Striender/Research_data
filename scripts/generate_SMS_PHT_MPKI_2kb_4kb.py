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
    "llama2.c-stories110M.1",
    "llama2.c-stories110M.2",
    "llama2.c-stories110M.3",
    "llama2.c-stories15M.1",
    "llama2.c-stories15M.2",
    "llama2.c-stories15M.3",
    "llama2.c-stories42M.1",
    "llama2.c-stories42M.2",
    "llama2.c-stories42M.3",
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

# 2KB data
data_2kb = [
    3.79385, 4.41543, 4.59212, 19.8401, 0.57175, 0.972045,
    4.48529, 4.0586, 2.48727, 5.71404, 3.32428, 6.26044,
    2.39356, 3.75003, 2.68682, 3.57618, 2.62474, 4.66428,
    8.11665, 7.41517, 2.62506, 0.74164, 1.61423, 5.16982,
    2.78678, 5.05443
]

# 4KB data
data_4kb = [
    2.97604, 3.69148, 3.97866, 17.5503, 0.32735, 0.682515,
    2.52055, 2.27071, 1.45246, 4.06506, 2.94859, 4.17617,
    1.42406, 2.19891, 1.61061, 3.31449, 2.07703, 3.9281,
    7.21951, 6.47429, 2.06929, 0.47046, 1.27306, 4.20574,
    2.22592, 4.21907
]

# 8KB data
data_8kb = [
    2.72531, 3.38905, 3.5579, 16.347, 0.251875, 0.607815,
    2.37345, 2.23416, 1.74314, 3.92519, 3.16679, 4.10099,
    2.16336, 2.78205, 2.19567, 4.16409, 1.63112, 3.66459,
    6.75558, 6.12253, 1.47542, 0.447845, 1.28591, 3.6343,
    1.52894, 3.76912
]

# Validate that every dataset matches the workload count
assert len(data_2kb) == len(workloads)
assert len(data_4kb) == len(workloads)
assert len(data_8kb) == len(workloads)

# Calculate averages
avg_2kb = np.mean(data_2kb)
avg_4kb = np.mean(data_4kb)
avg_8kb = np.mean(data_8kb)

# Append average
plot_workloads = workloads + ["Average"]
plot_2kb = data_2kb + [avg_2kb]
plot_4kb = data_4kb + [avg_4kb]
plot_8kb = data_8kb + [avg_8kb]

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

# Grouped bar setup
n = len(plot_workloads)
x = np.arange(n)

# Smaller width to accommodate three bars
bar_width = 0.27

fig, ax = plt.subplots()

# Colors
color_2kb = '#8C9EBC'
color_4kb = '#394761'
color_8kb = '#B5BFCF'

# Three bars centered around each workload position
bars1 = ax.bar(
    x - bar_width,
    plot_2kb,
    bar_width,
    label='2KB',
    color=color_2kb,
    edgecolor='black',
    linewidth=0.5
)

bars2 = ax.bar(
    x,
    plot_4kb,
    bar_width,
    label='4KB',
    color=color_4kb,
    edgecolor='black',
    linewidth=0.5
)

bars3 = ax.bar(
    x + bar_width,
    plot_8kb,
    bar_width,
    label='8KB',
    color=color_8kb,
    edgecolor='black',
    linewidth=0.5
)

# Axis labels
ax.set_ylabel('L2C MPKI')

ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=45, ha='right')

# Y-axis limits and ticks
ax.set_xlim(-1.0, n)
ax.set_ylim(0, 8)
ax.yaxis.set_major_locator(MultipleLocator(2))
ax.yaxis.set_minor_locator(MultipleLocator(1))
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

out_png = os.path.join(root_dir, 'SMS_PHT_MPKI_2kb_4kb_8kb.png')
out_pdf = os.path.join(root_dir, 'SMS_PHT_MPKI_2kb_4kb_8kb.pdf')

plt.savefig(out_png, bbox_inches='tight')
plt.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Saved: {out_png}")
print(f"Saved: {out_pdf}")
print(f"Average 2KB: {avg_2kb:.4f}%")
print(f"Average 4KB: {avg_4kb:.4f}%")
print(f"Average 8KB: {avg_8kb:.4f}%")
