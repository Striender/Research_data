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

# 2KB data
data_2kb = [
84.7327,
83.8960,
79.5038,
64.5605,
94.4940,
93.3081,
95.0357,
95.4726,
95.6924,
95.7837,
95.6641,
95.8915,
95.6132,
95.8553,
96.0155,
85.2598,
92.6002,
79.0988,
51.1762,
68.0253,
93.5949,
93.2126,
90.0623,
55.1883,
90.2357,
51.3318



]

# 4KB data
data_4kb = [
    12.92514518,
10.73270961,
16.27130168,
32.78040148,
1.484866094,
2.736023318,
1.083578322,
0.732425307,
1.249400793,
0.523598744,
0.874312383,
0.60973472,
1.022649082,
0.915187349,
0.583398413,
4.797736746,
3.731565571,
14.27025125,
42.89274738,
27.58943151,
3.636997116,
1.507695302,
4.523248126,
41.76693181,
4.784705731,
45.12634219
]

# 8KB data
data_8kb = [
2.307740918,
5.336380227,
4.188127856,
2.653730297,
3.91316346,
3.930438577,
3.8634837,
3.792144702,
3.053060806,
3.682775282,
3.453526724,
3.489966261,
3.358534583,
3.225273764,
3.399445972,
9.879576774,
3.611899491,
6.569805073,
5.88181683,
4.36330615,
2.748999783,
5.188161427,
5.376293757,
2.95977294,
4.86996213,
3.463992917

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
color_2kb = '#8C9EBC'
color_4kb = '#394761'
color_8kb = '#B5BFCF'

# Three bars centered around each workload position
bars1 = ax.bar(
    x - bar_width,
    plot_2kb,
    bar_width,
    label='L1D',
    color=color_2kb,
    edgecolor='black',
    linewidth=0.5
)

bars2 = ax.bar(
    x,
    plot_4kb,
    bar_width,
    label='L2',
    color=color_4kb,
    edgecolor='black',
    linewidth=0.5
)

bars3 = ax.bar(
    x + bar_width,
    plot_8kb,
    bar_width,
    label='LLC',
    color=color_8kb,
    edgecolor='black',
    linewidth=0.5
)

# Axis labels
ax.set_ylabel('MPKI')

ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=45, ha='right')

# Y-axis limits and ticks
ax.set_xlim(-1.0, n)
ax.set_ylim(0, 40)
ax.yaxis.set_major_locator(MultipleLocator(10))
ax.yaxis.set_minor_locator(MultipleLocator(2.5))
ax.tick_params(which='minor', length=2, color='black')

# Annotate bars that exceed the y-limit of 100 using arrows with 90-degree rotated labels
ylim_max = ax.get_ylim()[1]
for rect in list(bars1) + list(bars2) + list(bars3):
    height = rect.get_height()
    if height > ylim_max:
        bar_x = rect.get_x() + rect.get_width() / 2.0
        ax.annotate(
            f'{height:.2f}',
            xy=(bar_x, ylim_max),
            xytext=(0, 10),
            textcoords='offset points',
            arrowprops=dict(arrowstyle="->", color='black', lw=0.5, shrinkA=0, shrinkB=1),
            ha='center',
            va='bottom',
            fontsize=3.0 * scale,
            color='black',
            rotation=90
        )

# Legend
ax.legend(
    loc='lower right',
    bbox_to_anchor=(0.53, 1.02),
    ncol=3,
    #title='Cache Level',
    title_fontsize=4.0 * scale,
    frameon=True,
    facecolor='white',
    edgecolor='black',
    framealpha=1.0,
    fancybox=False
)

root_dir = "../plots/Pref/MPKI"
os.makedirs(root_dir, exist_ok=True)

out_png = os.path.join(root_dir, 'Berti_MPKI_l1+l2+llc.png')
out_pdf = os.path.join(root_dir, 'Berti_MPKI_l1+l2+llc.pdf')

plt.savefig(out_png, bbox_inches='tight')
plt.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Saved: {out_png}")
print(f"Saved: {out_pdf}")
print(f"Average 2KB: {avg_2kb:.4f}%")
print(f"Average 4KB: {avg_4kb:.4f}%")
print(f"Average 8KB: {avg_8kb:.4f}%")
