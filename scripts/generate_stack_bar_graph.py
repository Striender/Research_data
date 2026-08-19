import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
import os
import textwrap

# AI/ML Workloads (26 items + Average)
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
    "Average"
]

# Raw Data definitions (5-bin)
cat_1_30 = [84.7327,
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
cat_31_60 = [12.92514518,
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
cat_61_90 = [
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
#cat_91_120 = [
#]

# Calculate averages dynamically
avg_1_30 = sum(cat_1_30) / len(cat_1_30)
avg_31_60 = sum(cat_31_60) / len(cat_31_60)
avg_61_90 = sum(cat_61_90) / len(cat_61_90)
#avg_91_120 = sum(cat_91_120) / len(cat_91_120)


y_data = [
    np.array(cat_1_30 + [avg_1_30]),
    np.array(cat_31_60 + [avg_31_60]),
    np.array(cat_61_90 + [avg_61_90]),
    #np.array(cat_91_120 + [avg_91_120])
]


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

# Columns labels for legend (without %)
labels = [
    'Usefull Prefetches',
    'Late Prefetches',
    'Useless Prefetches',
    #'Fill L2'
]

# Monochromatic colors as requested
mono_colors = [
    '#C5D3E8',  # EMISSARY
    '#52688F',  # ICARUS
    '#394761',  # SWING
    '#262f40'   # Ideal L2
]

# Set spacing to 0.28, and keep bar width strictly at 0.18 (gap = 0.10)
spacing = 0.28
x_indices = np.arange(len(workloads)) * spacing
width = 0.18  # Kept strictly at 0.18

fig, ax = plt.subplots()

bottom = np.zeros(len(workloads))
for i in range(3):
    ax.bar(x_indices, y_data[i], width, bottom=bottom, label=labels[i], color=mono_colors[i], edgecolor='black', linewidth=0.5)
    bottom = bottom + y_data[i]

# Labeling and details with dynamic wrapping
y_label_text = 'Percentage of prefetch \n issued from L2'
wrapped_y_label = "\n".join(textwrap.wrap(y_label_text, width=20))
ax.set_ylabel(y_label_text, labelpad=10, fontsize=5.0 * scale)

# No x axis label
ax.set_xlabel(None)

ax.set_xticks(x_indices)
ax.set_xticklabels(workloads, rotation=45, ha='right')

# Set y-axis ticks of 20
ax.yaxis.set_major_locator(MultipleLocator(20))

ax.set_xlim(-spacing, x_indices[-1] + spacing)
ax.set_ylim(0, 100)

# Legend expanded to match exactly the active plot area width, with narrow box and small font size to prevent overlapping
ax.legend(loc='lower left', bbox_to_anchor=(0.0, 1.02, 1.0, 0.1), mode="expand", ncol=5, frameon=True, facecolor='white', edgecolor='black', framealpha=1.0, fancybox=False, handlelength=1.0, handletextpad=0.3, fontsize=5.0 * scale)

sample_dir = "../plots/bingo/"
os.makedirs(sample_dir, exist_ok=True)

plt.savefig(os.path.join(sample_dir, 'distribution_of_pf_requests.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, 'distribution_of_pf_requests.pdf'), bbox_inches='tight')
plt.close()

print("Successfully generated stacked bar sample plot with font size 15.")