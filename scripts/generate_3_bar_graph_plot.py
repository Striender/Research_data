from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator

# AI/ML Workloads (26 items)
workloads = [
    #"bark.cpp-bark.1",
    #"bark.cpp-bark.2",
    #"bark.cpp-bark.4",
    #"bark.cpp-bark.5",
    #"clip_trace_1",
    #"clip_trace_3",
    #"llama2.c-stories15M.1",
    #"llama2.c-stories15M.2",
    #"llama2.c-stories15M.3",
    #"llama2.c-stories42M.1",
    #"llama2.c-stories42M.2",
    #"llama2.c-stories42M.3",
    #"llama2.c-stories110M.1",
    #"llama2.c-stories110M.2",
    #"llama2.c-stories110M.3",
    #"stable-diffusion.1",
    #"stable-diffusion.2",
    #"stable-diffusion.v1-5",
    #"stable-diffusion.v2-1_768.1",
    #"stable-diffusion.v2-1_768.2",
    #"stable-diffusion.v2-1_768.3",
    #"vit.cpp-base-f16",
    #"vit.cpp-large-f16",
    #"whisper_trace_1",
    #"whisper_trace_2",
    #"whisper_trace_3"

    "bark.coarse_token_gen.1",
    "bark.coarse_token_gen.2",
    "bark.coarse_token_gen.3",
    "bark.coarse_token_gen.4",
    "bark.coarse_token_gen.5",
    "bark.semantic_token_gen.1",
    "bark.semantic_token_gen.2",
    "bark.semantic_token_gen.3",
    "bark.semantic_token_gen.4",
    "bark.semantic_token_gen.5",
    "clip_trace_1",
    "clip_trace_2",
    "clip_trace_3",
    "clip_trace_4",
    "clip_trace_5",
    "llama2.c-llama2_7b.1",
    "llama2.c-llama2_7b.10",
    "llama2.c-llama2_7b.11",
    "llama2.c-llama2_7b.12",
    "llama2.c-llama2_7b.13",
    "llama2.c-llama2_7b.14",
    "llama2.c-llama2_7b.15",
    "llama2.c-llama2_7b.16",
    "llama2.c-llama2_7b.2",
    "llama2.c-llama2_7b.3",
    "llama2.c-llama2_7b.4",
    "llama2.c-llama2_7b.6",
    "llama2.c-llama2_7b.7",
    "llama2.c-llama2_7b.8",
    "llama2.c-llama2_7b.9",
    "llama2.c-stories110M.1",
    "llama2.c-stories110M.2",
    "llama2.c-stories110M.3",
    "llama2.c-stories15M.1",
    "llama2.c-stories15M.2",
    "llama2.c-stories15M.3",
    "llama2.c-stories42M.1",
    "llama2.c-stories42M.2",
    "llama2.c-stories42M.3",
    "sd.cpp-sd-v1-4.ckpt.1",
    "sd.cpp-sd-v1-4.ckpt.2",
    "sd.cpp-sd-v1-4.ckpt.3",
    "sd.cpp-sd-v1-4.ckpt.4",
    "sd.cpp-sd-v1-4.ckpt.5",
    "sd.cpp-v1-5-pruned-emaonly.1",
    "sd.cpp-v1-5-pruned-emaonly.2",
    "sd.cpp-v1-5-pruned-emaonly.3",
    "sd.cpp-v1-5-pruned-emaonly.4",
    "sd.cpp-v1-5-pruned-emaonly.5",
    "sd.cpp-v2-1_768-nonema-pruned.1",
    "sd.cpp-v2-1_768-nonema-pruned.2",
    "sd.cpp-v2-1_768-nonema-pruned.3",
    "sd.cpp-v2-1_768-nonema-pruned.4",
    "sd.cpp-v2-1_768-nonema-pruned.5",
    "vit.cpp-base-ggml-model.1",
    "vit.cpp-base-ggml-model.2",
    "vit.cpp-large-ggml-model.1",
    "vit.cpp-large-ggml-model.2",
    "vit.cpp-large-ggml-model.3",
    "vit.cpp-large-ggml-model.4",
    "whisper_trace_1",
    "whisper_trace_2",
    "whisper_trace_3",
    "whisper_trace_4",
    "whisper_trace_5",
    "whisper_trace_6",
    "whisper_trace_7",
    "whisper_trace_8",
    #"Geomean"

    
]

# 2KB data
data_2kb = [ 0.571285,
1.71386,
0.302265,
1.76045,
12.29943,
1.58811,
0.27755,
11.018515,
11.63559,
12.219725,
0.84341,
0.41345,
0.929935,
1.325805,
0.692465,
0.00126,
0.064775,
0.135245,
0.08312,
0.107885,
0.00288,
0.133595,
0.122735,
0.135865,
0.002535,
0.08569,
0.003225,
0.083915,
0.130165,
0.01505,
0.056795,
0.060925,
0.06857,
0.023055,
0.03501,
0.030835,
0.02331,
0.020785,
0.01518,
1.125325,
1.023825,
0.01248,
1.927735,
0.5367,
0.01248,
1.284375,
4.56511,
1.01429,
0.016975,
2.575155,
0.58356,
1.009275,
0.463225,
1.88878,
2.294985,
0.9761,
0.98445,
0.63422,
0.48891,
0.717965,
0.84582,
1.571945,
1.35469,
1.869515,
4.40534,
6.67697,
2.019535,
1.13827

]
# 4KB data,,
data_4kb = [
3.6361    ,
4.795995,
1.07399,
4.323345,
13.644565,
4.148855,
3.47417,
17.157565,
15.82737,
14.36916,
2.90442,
1.6799,
3.27575,
2.87117,
3.232695,
34.50613,
33.643155,
32.84631,
33.567015,
33.018935,
34.339485,
32.836665,
33.126865,
32.71094,
34.399705,
33.57426,
34.383495,
33.56132,
32.85081,
34.293755,
32.31672,
31.634235,
31.584805,
33.66062,
33.57578,
33.650655,
33.82102,
33.820645,
33.83989,
4.432875,
3.068475,
0.058335,
3.73187,
4.979625,
0.00797,
3.69713,
2.727905,
3.03479,
0.00957,
0.70536,
2.886295,
3.043905,
3.15723,
2.34496,
3.64507,
2.18099,
3.623815,
2.91116,
0.909125,
2.902835,
2.18521,
2.30667,
2.19354,
6.79853,
1.898085,
0.39769,
6.333315,
3.99551
]
# 8KB data,
data_8kb = [
1.433005 ,
1.4034,
0.46794,
1.863185,
0,
2.00907,
0.989275,
0.006815,
0,
0,
0,
0.405335,
0.11291,
0.529475,
0.4917,
0.010895,
0,
0,
0.01231,
0,
0,
0.05683,
0,
0.042315,
0,
0,
0,
0,
0.00891,
0.000075,
0,
0,
0.00026,
0,
0,
0.01394,
0.014475,
0,
0.00419,
1.97388,
0,
0.035835,
0.000455,
0,
0.0019,
0.858725,
1.88353,
0,
0.002885,
4.480225,
0,
0.00548,
0.074755,
0.23095,
1.741745,
0.423045,
0.948965,
1.62008,
0.21756,
0.82388,
0,
0,
0,
0,
0.024785,
0,
0,
0.385985

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
x_spacing = 1.35
fig_width_pt = 240.94499
inches_per_pt = 1.0 / 72.27
golden_mean = 0.6
fig_width = fig_width_pt * inches_per_pt * scale * x_spacing

params = {
    'figure.dpi': 300,
    'backend': 'ps',
    'axes.labelsize': 5.0 * scale,
    'font.size': 5.0 * scale,
    'legend.fontsize': 4.0 * scale,
    'xtick.labelsize': 3.5 * scale,
    'ytick.labelsize': 4.0 * scale,
    'text.usetex': False,
    'font.family': 'serif',
    #'font.serif': ['Times', 'Times New Roman', 'Liberation Serif'],
    'patch.linewidth': 0.5,
    'patch.edgecolor': 'black',
    'figure.figsize': [fig_width, fig_width * golden_mean * 0.65],
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
x = np.arange(n) * x_spacing

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
ax.set_ylabel('Useless prefetches per\n kilo instructions ', fontsize=3.5 * scale)

ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=90)

# Y-axis limits and ticks
ax.set_xlim(-x_spacing, x[-1] + x_spacing)
ax.set_ylim(0,12)
ax.yaxis.set_major_locator(MultipleLocator(2))
ax.yaxis.set_minor_locator(MultipleLocator(1))
ax.tick_params(which='minor', length=2, color='black')

# Annotate bars that exceed the y-limit of 100 using arrows with 90-degree rotated labels
# ── Collision-safe annotations for bars exceeding ylim ───────────────────────
ylim_max = ax.get_ylim()[1]

# Collect all bars that exceed the y limit
overflow_bars = []
for rect in list(bars1) + list(bars2) + list(bars3) :
    height = rect.get_height()
    if height > ylim_max:
        bar_x = rect.get_x() + rect.get_width() / 2.0
        overflow_bars.append((bar_x, height))

# Sort left-to-right so stacking order is consistent within each group
overflow_bars.sort(key=lambda t: t[0])

# Track stagger level per x-group (identified by rounded bar_x)
stagger_count = defaultdict(int)
text_step_pts = 15   # vertical gap in points between stacked labels

for bar_x, height in overflow_bars:
    group_key = round(bar_x)
    level = stagger_count[group_key]
    stagger_count[group_key] += 1

    y_offset = 8 + level * text_step_pts  # 1st: 8pt, 2nd: 22pt, 3rd: 36pt …

    ax.annotate(
        f'{height:.2f}',
        xy=(bar_x, ylim_max),
        xytext=(0, y_offset),
        textcoords='offset points',
        arrowprops=dict(
            arrowstyle="->",
            color='black',
            lw=0.3,
            shrinkA=0,
            shrinkB=1
        ),
        
        ha='center',
        va='bottom',
        fontsize=3 * scale,
        color='black',
        rotation=90,
        clip_on=False
    )


# Legend
ax.legend(
    loc='lower left',
    bbox_to_anchor=(0.60, 1.02),
    ncol=3,
    #title='Cache Level',
    title_fontsize=4.0 * scale,
    frameon=True,
    facecolor='white',
    edgecolor='black',
    framealpha=1.0,
    fancybox=False
)

root_dir = "../plots/aiml_bingo/"
os.makedirs(root_dir, exist_ok=True)

out_png = os.path.join(root_dir, 'bingo+bingo_useless_prefetches_l1+l2+llc.png')
#out_pdf = os.path.join(root_dir, 'Berti_Accuracy_l1+l2+llc.pdf')
#out_svg = os.path.join(root_dir, 'bingo+bingo_MPKI_l1+l2+llc.svg')

#plt.savefig(out_svg, bbox_inches='tight')
plt.savefig(out_png, bbox_inches='tight')
#plt.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Saved: {out_png}")
#print(f"Saved: {out_pdf}")
print(f"Average 2KB: {avg_2kb:.4f}%")
print(f"Average 4KB: {avg_4kb:.4f}%")
print(f"Average 8KB: {avg_8kb:.4f}%")
