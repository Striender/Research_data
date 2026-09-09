import matplotlib.pyplot as plt
import numpy as np
import os
# SPEC Workloads (41 items + Average)
workloads = [
   
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
        "Average"
]

data = [58.2288,
86.5596,
67.8362,
85.7148,
7.2964,
84.2720,
65.2575,
7.9319,
6.1437,
7.3245,
72.2353,
80.1704,
67.9678,
62.0534,
77.0810,
92.8313,
91.5673,
90.8235,
91.4334,
91.1985,
92.9259,
90.7676,
90.8649,
90.8404,
92.9566,
91.4032,
92.8483,
91.4245,
90.7104,
92.4723,
93.3932,
93.2588,
93.4453,
93.3363,
93.2437,
93.2566,
93.1621,
93.1798,
93.0766,
91.1115,
91.9539,
90.0344,
90.2867,
81.5035,
90.3033,
91.5684,
77.4463,
91.5852,
90.0568,
74.3207,
89.3982,
91.6189,
81.9379,
90.6957,
88.3650,
67.4534,
87.7802,
75.3536,
72.6327,
74.5177,
56.1640,
56.7674,
55.6202,
74.3053,
77.5618,
79.6402,
73.1138,
65.6445,
78.95933824
]

# Calculate arithmetic average
avg_val = sum(data) / len(data)

# Set parameters according to workspace styles
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
    'xtick.labelsize': 2.7 * scale,
    'ytick.labelsize': 4.0 * scale,
    'text.usetex': False,
    'font.family': 'serif',
    #'font.serif': ['Times', 'Times New Roman', 'Liberation Serif'],
    'patch.linewidth': 0.5,
    'patch.edgecolor': 'black',
    'figure.figsize': [fig_width, fig_width * golden_mean * 0.75],
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

# Create figure
x_indices = np.arange(len(workloads))
width = 0.6  # Width of the bars

fig, ax = plt.subplots()

# Colors mapping to the palette:
# Use #52688F for standard workload bars, and #262f40 for the Average bar
colors_list = ["#8C9EBC"] * (len(workloads) - 1) + ['#262f40']   #86A4DA (GOOD COLOUR)

# Draw bars
rects = ax.bar(x_indices, data, width, color=colors_list, edgecolor='black', linewidth=0.5)

# Labeling and details
ax.set_ylabel('L1D Prefetcher \nAccuracy (%)', fontsize=4.0 * scale)
#ax.set_xlabel('SPEC Workload')  
ax.set_xticks(x_indices)
ax.set_xticklabels(workloads, rotation=90)


# Baseline reference line at y = 1.0
#ax.axhline(y=1.0, color='black', linewidth=0.65, linestyle='--', zorder=5)

# Adjust limits (set y limit to 100 as requested)
ylim_max = 100
ax.set_xlim(-1.0, len(workloads))
ax.set_ylim(0,ylim_max)

# Set y-axis ticks (major ticks every 10, minor ticks every 2)
from matplotlib.ticker import MultipleLocator
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.yaxis.set_minor_locator(MultipleLocator(10))
ax.tick_params(which='minor', length=2, color='black')

# Annotate bars that exceed the y-limit of 100 using arrows with 90-degree rotated labels

for rect in rects:
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
out_name = 'Bingo_prefetch_accuracy'
sample_dir = "../plots/aiml_bingo/"
os.makedirs(sample_dir, exist_ok=True)

plt.savefig(os.path.join(sample_dir, f'{out_name}.svg'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
#plt.savefig(os.path.join(sample_dir, f'{out_name}.pdf'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print("Calculated Average: {:.4f}".format(avg_val))