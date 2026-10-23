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
    "llama2.c-llama2_7b.2",
    "llama2.c-llama2_7b.3",
    "llama2.c-llama2_7b.4",
    "llama2.c-llama2_7b.6",
    "llama2.c-llama2_7b.7",
    "llama2.c-llama2_7b.8",
    "llama2.c-llama2_7b.9",
    "llama2.c-llama2_7b.10",
    "llama2.c-llama2_7b.11",
    "llama2.c-llama2_7b.12",
    "llama2.c-llama2_7b.13",
    "llama2.c-llama2_7b.14",
    "llama2.c-llama2_7b.15",
    "llama2.c-llama2_7b.16",
    "llama2.c-stories15M.1",
    "llama2.c-stories15M.2",
    "llama2.c-stories15M.3",
    "llama2.c-stories42M.1",
    "llama2.c-stories42M.2",
    "llama2.c-stories42M.3",
    "llama2.c-stories110M.1",
    "llama2.c-stories110M.2",
    "llama2.c-stories110M.3",
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
        "Geomean"
]

data = [
    1.025142921,
1.010058164,
1.024061634,
1.03477979,
1.039778979,
1.031110606,
1.033831393,
1.08688761,
1.060767134,
1.034589615,
1.026019813,
0.9971266816,
1.026219986,
1.009575487,
1.005962032,
1.008552187,
1.010966692,
1.048215521,
1.041203823,
1.099424009,
0.9830139917,
1.039126798,
1.058845541,
1.020951869,
0.9781638662,
1.046569094,
0.9820166773,
1.06340031,
1.034835867,
1.01193091,
0.9221892933,
0.9278713152,
0.9274627512,
0.9138620909,
0.9185220877,
0.9189343371,
1.039659322,
1.042172077,
1.022184801,
1.036790685,
1.02574985,
0.9998499028,
1.061600156,
1.082551769,
0.9989244501,
1.006159084,
1.040253022,
1.026112735,
0.9987922002,
1.007388905,
1.023476964,
1.022527973,
1.056543039,
1.020132287,
1.008442202,
0.9912725816,
1.0252517,
1.017995341,
0.9744674943,
1.02243685,
1.027449805,
1.029018602,
1.031169812,
1.040186923,
1.031091596,
1.002833538,
1.039498589,
0.9903850887,
1.01609431
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
ax.set_ylabel('Speedup', fontsize=4.0 * scale)
#ax.set_xlabel('SPEC Workload')  
ax.set_xticks(x_indices)
ax.set_xticklabels(workloads, rotation=90)


# Baseline reference line at y = 1.0
ax.axhline(y=1.0, color='black', linewidth=0.65, linestyle='--', zorder=5)

# Adjust limits (set y limit to 100 as requested)
ylim_max = 1.2
ax.set_xlim(-1.0, len(workloads))
ax.set_ylim(0.8,ylim_max)

# Set y-axis ticks (major ticks every 10, minor ticks every 2)
from matplotlib.ticker import MultipleLocator
ax.yaxis.set_major_locator(MultipleLocator(0.1))
ax.yaxis.set_minor_locator(MultipleLocator(0.05))
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
out_name = 'Speedup_48KB_L1D_without_LLC_over_48KB_L1D_with_LLC'
sample_dir = "../plots/cache_sensitivity/without_llc/"
os.makedirs(sample_dir, exist_ok=True)

#plt.savefig(os.path.join(sample_dir, f'{out_name}.svg'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
#plt.savefig(os.path.join(sample_dir, f'{out_name}.pdf'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print("Calculated Average: {:.4f}".format(avg_val))