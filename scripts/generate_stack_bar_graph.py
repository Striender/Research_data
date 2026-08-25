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
cat_1_30 = [65.33112905,
67.499168,
3.997399995,
82.98267823,
0,
19.71893045,
100,
90.53254438,
67.25440806,
0,
61.78571429,
8.480565371,
0,
37.14285714,
0,
57.11042312,
60.24,
65.43939059,
43.74206834,
70.32930897,
55.37806177,
2.567520541,
81.18918919,
78.76712329,
94.21364985,
77.16998658,
53.5530871

]
cat_31_60 = [
0,
2.60490727,
73.2052622,
1.225824026,
0,
52.73088132,
0,
0,
0.856423174,
0,
0,
0,
0,
0,
0,
0,
0,
0,
22.06259129,
0,
0,
90.81932984,
0.135135135,
0,
0,
0,
8.356026548
]
cat_61_90 = [
  34.66887095,
29.71591081,
22.44771916,
15.78508821,
0,
27.32350054,
0,
9.467455621,
31.88916877,
100,
38.21428571,
91.51943463,
100,
62.85714286,
0,
42.88957688,
39.76,
34.56060941,
34.1737902,
29.57203927,
44.62193823,
6.443869035,
18.67567568,
21.23287671,
5.786350148,
22.83001342,
38.09088636
]
#cat_91_120 = [
#]

# Calculate averages dynamically
avg_1_30 = sum(cat_1_30) / len(cat_1_30)
avg_31_60 = sum(cat_31_60) / len(cat_31_60)
avg_61_90 = sum(cat_61_90) / len(cat_61_90)
#avg_91_120 = sum(cat_91_120) / len(cat_91_120)


y_data = [
    np.array(cat_1_30),
    np.array(cat_31_60),
    np.array(cat_61_90),
    #np.array(cat_91_120 + [avg_91_120])
]

#when average is needed to be calculated
#y_data = [
#    np.array(cat_1_30 + [avg_1_30]),
#    np.array(cat_31_60 + [avg_31_60]),
#    np.array(cat_61_90 + [avg_61_90]),
#    #np.array(cat_91_120 + [avg_91_120])
#]
#


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
    'Load',
    'RFO',
    'Prefetches',
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
y_label_text = 'Distribution of request blocked \nwhen MSHR is Full'
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
ax.legend(loc='lower center', bbox_to_anchor=(0.0, 1.02, 1.0, 0.1), ncol=5, frameon=True , facecolor='white', edgecolor='black', framealpha=1.0, fancybox=False, handlelength=1.0, handletextpad=0.3, fontsize=5.0 * scale, title='Request Type',) #add , mode="expand" to expand the 

sample_dir = "../plots/Pref/Mshr_full"
os.makedirs(sample_dir, exist_ok=True)

plt.savefig(os.path.join(sample_dir, 'distribution_of_bingo-l2_MSHR_Full_events.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, 'distribution_of_bingo-l2_MSHR_Full_events.pdf'), bbox_inches='tight')
plt.close()

print("Successfully generated stacked bar sample plot with font size 15.")