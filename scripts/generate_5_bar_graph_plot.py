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

# ── DATA (26 values each, already ordered per workload list above) ────────────
data_bar1 = [54.7635,
82.8719,
80.8242,
15.0715,
92.3367,
91.6683,
79.2718,
91.9099,
74.369,
93.2766,
85.3834,
91.4649,
82.511,
84.7714,
92.7596,
93.3135,
90.4985,
81.9991,
53.1457,
85.7377,
90.4525,
92.9464,
83.9961,
60.408,
73.3028,
66.0985
]  
data_bar2 = [
   60.583,
86.8577,
85.1726,
13.4124,
93.7475,
93.4361,
89.6272,
95.2841,
87.2222,
96.555,
92.8545,
95.6585,
91.1246,
92.2852,
95.9957,
96.3153,
94.6119,
89.5309,
68.8497,
92.3279,
94.5872,
93.6256,
87.4904,
79.9636,
81.2695,
79.4988
] 
data_bar3 = [
    59.9582,
87.6842,
87.2634,
27.6772,
90.4746,
92.0137,
94.5502,
96.9781,
93.6123,
98.0558,
96.0112,
97.5256,
95.3039,
95.9357,
97.5546,
97.9995,
96.217,
93.6655,
75.3813,
93.458,
96.1779,
92.0957,
89.2478,
73.6055,
86.8746,
76.8892
] 
data_bar4 = [52.0092,
88.7935,
88.2413,
47.7026,
43.9315,
53.6295,
96.4751,
97.9682,
95.406,
98.8358,
97.358,
98.471,
95.2299,
95.9565,
97.9851,
98.5947,
95.1174,
95.5268,
79.9194,
87.0398,
95.0383,
91.4026,
82.2233,
44.5785,
29.8491,
47.7813
] 
data_bar5 = [
  21.3911,
88.1368,
87.7259,
59.7893,
32.0793,
43.4139,
96.8207,
97.0395,
95.6013,
99.2462,
98.2115,
98.0296,
95.2135,
96.1788,
98.1255,
98.7321,
95.194,
96.5276,
84.3207,
87.2689,
95.2642,
84.1172,
79.8065,
42.4517,
22.131,
37.6829
] 

# ── LABELS (shown in legend) ──────────────────────────────────────────────────
label_bar1 = '1 KB'
label_bar2 = '2 KB'
label_bar3 = '4 KB'
label_bar4 = '8 KB'
label_bar5 = '16 KB'

# ── LEGEND TITLE ──────────────────────────────────────────────────────────────
legend_title = 'Region size'

# ── Y-AXIS LABEL ──────────────────────────────────────────────────────────────
ylabel = 'L1D Accuracy (%)'

# ── OUTPUT FILENAME (no extension) ───────────────────────────────────────────
out_name = 'Bingo_l1d_accuracy'

# ─────────────────────────────────────────────────────────────────────────────

# Calculate averages
all_data   = [data_bar1, data_bar2, data_bar3, data_bar4, data_bar5]
all_labels = [label_bar1, label_bar2, label_bar3, label_bar4, label_bar5]

plot_workloads = workloads + ["Average"]
plot_data = [d + [np.mean(d)] for d in all_data]

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

# Grouped bar setup — 5 bars, centered around each x position
n = len(plot_workloads)
x = np.arange(n)
bar_width = 0.16   # 5 bars × 0.16 = 0.80 total group width

# Colors from palette (light → dark)
colors = ['#F3F3F3', '#C5D3E8', '#8C9EBC', '#52688F', '#262f40']

fig, ax = plt.subplots()

for i, (d, c, lbl) in enumerate(zip(plot_data, colors, all_labels)):
    offset = (-2 + i) * bar_width
    ax.bar(x + offset, d, bar_width, label=lbl, color=c, edgecolor='black', linewidth=0.5)

ax.set_ylabel(ylabel)
ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=45, ha='right')
ax.set_xlim(-1.0, n)
ax.set_ylim(0, 100)
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.yaxis.set_minor_locator(MultipleLocator(5))
ax.tick_params(which='minor', length=2, color='black')

ax.legend(
    loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=5,
    title=legend_title, title_fontsize=4.0 * scale,
    frameon=True, facecolor='white', edgecolor='black',
    framealpha=1.0, fancybox=False
)

sample_dir = "../plots/bingo/"
os.makedirs(sample_dir, exist_ok=True)

plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.pdf'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
for lbl, d in zip(all_labels, all_data):
    print(f"Average {lbl}: {np.mean(d):.4f}%")
