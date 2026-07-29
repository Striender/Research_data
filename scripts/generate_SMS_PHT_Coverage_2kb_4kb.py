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
    36.5925994,
37.45235905,
35.98897959,
19.76489691,
84.32930523,
78.48344054,
87.17974992,
88.40077604,
92.89122323,
83.04023479,
89.9334892,
81.02412432,
93.09818938,
89.17135074,
92.24930367,
77.62264082,
66.6239836,
45.53101967,
22.2185594,
18.63215169,
66.40019967,
83.37219522,
61.59249945,
21.69725802,
57.77273361,
23.48330596
]

# 4KB data
data_4kb = [50.26080925,
47.70760336,
44.54025392,
29.02509155,
91.02789343,
84.89228937,
92.79552014,
93.51046139,
95.84877641,
87.93453529,
91.07115874,
87.34171729,
95.89372026,
93.65037632,
95.35385156,
79.26006275,
73.58867725,
54.1280445,
30.81576339,
28.95652379,
73.5138508,
89.4521371,
69.7098901,
36.29932047,
66.27135774,
36.1293741
]

# 8KB data
data_8kb = [
    54.4513897,
51.99173008,
50.40535492,
33.89114122,
93.09653477,
86.54580026,
93.21598905,
93.61490458,
95.01800866,
88.34968155,
90.4103962,
87.56957832,
93.76198361,
91.96650596,
93.66612631,
73.9438541,
79.25882786,
57.20528378,
35.26158352,
32.81655235,
81.11516788,
89.9591726,
69.40426706,
44.95448972,
76.8324171,
42.9410429
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
ax.set_ylabel('Coverage (%)')

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

out_png = os.path.join(root_dir, 'SMS_PHT_Coverage_2kb_4kb_8kb.png')
out_pdf = os.path.join(root_dir, 'SMS_PHT_Coverage_2kb_4kb_8kb.pdf')

plt.savefig(out_png, bbox_inches='tight')
plt.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Saved: {out_png}")
print(f"Saved: {out_pdf}")
print(f"Average 2KB: {avg_2kb:.4f}%")
print(f"Average 4KB: {avg_4kb:.4f}%")
print(f"Average 8KB: {avg_8kb:.4f}%")
