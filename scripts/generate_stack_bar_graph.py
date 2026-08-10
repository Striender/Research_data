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
cat_1_30 = [19.5181501830914,
35.0840308816998,
38.2024857676647,
22.0968877675546,
55.1981632786786,
53.2270839569129,
52.6008358999444,
54.4701326053519,
51.9038627087872,
55.3221051524555,
53.2215255067855,
54.6494824918367,
52.4166336472915,
53.5367050677199,
55.1024140575284,
55.758439813694,
59.3792813634327,
53.2307466616386,
38.2756069006649,
53.9584056950523,
58.9911395480811,
55.1227181115359,
46.5524798457147,
9.37847412655826,
71.9047791996061,
9.07651448625726
]
cat_31_60 = [7.87052052325277,
9.06987391774781,
10.433440212173,
2.85212383844184,
0.381726202177116,
1.09821093033535,
0.0435048820765965,
0.101502116154227,
0.223675572529453,
0.0156402631609107,
0.0240600175345608,
0.0777823845578868,
0.0149180473020756,
0.0241760347073311,
0.020859903986197,
0.0986226550713049,
1.3614601713939,
0.251518570784761,
16.3118773607828,
0.121438132676804,
1.28452726994192,
1.11910031564368,
1.48731235031056,
7.29420406576774,
5.10687925489199,
6.35121945249322
]
cat_61_90 = [41.699233488862,
33.4232600984541,
31.2899710612521,
60.7292579400221,
3.52827915744694,
4.52522031510042,
2.92363767257358,
1.10405580958713,
3.50188151968986,
1.09319203613979,
2.35346474253198,
1.36110369321695,
2.70455277854564,
2.36654766639063,
1.09094718442052,
1.86233281480059,
6.1408714631516,
4.76758088122764,
7.9537673124075,
3.33103648610954,
5.79776950853024,
2.81584951216268,
18.1830397506045,
67.0637567588489,
22.7757533201777,
66.3095460289389
]
cat_91_120 = [30.9120958047939,
22.4228351020984,
20.0741029589102,
14.3217304539814,
40.8918313616973,
41.1494847976514,
44.4320215454054,
44.3243094689068,
44.3705801989935,
43.5690625482438,
44.400949733148,
43.9116314303885,
44.8638955268608,
44.0725712311822,
43.7857788540649,
42.2806047164341,
33.1183870020218,
41.750153886349,
37.4587484261448,
42.5891196861613,
33.9265636734467,
40.9423320606578,
33.7771680533702,
16.2635650488251,
0.212588225324149,
18.2627200323107
]

# Calculate averages dynamically
avg_1_30 = sum(cat_1_30) / len(cat_1_30)
avg_31_60 = sum(cat_31_60) / len(cat_31_60)
avg_61_90 = sum(cat_61_90) / len(cat_61_90)
avg_91_120 = sum(cat_91_120) / len(cat_91_120)


y_data = [
    np.array(cat_1_30 + [avg_1_30]),
    np.array(cat_31_60 + [avg_31_60]),
    np.array(cat_61_90 + [avg_61_90]),
    np.array(cat_91_120 + [avg_91_120])
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
    'Useless Prefetches',
    'Late Prefetches',
    'Fill L2'
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
for i in range(4):
    ax.bar(x_indices, y_data[i], width, bottom=bottom, label=labels[i], color=mono_colors[i], edgecolor='black', linewidth=0.5)
    bottom = bottom + y_data[i]

# Labeling and details with dynamic wrapping
y_label_text = 'Percentage of prefetch issued'
wrapped_y_label = "\n".join(textwrap.wrap(y_label_text, width=20))
ax.set_ylabel(wrapped_y_label)

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

sample_dir = "../plots/"
os.makedirs(sample_dir, exist_ok=True)

plt.savefig(os.path.join(sample_dir, 'L1d_mshr_cycle_occupancy_mono_stacked_bar.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, 'L1d_mshr_cycle_occupancy_mono_stacked_bar.pdf'), bbox_inches='tight')
plt.close()

print("Successfully generated stacked bar sample plot with font size 15.")