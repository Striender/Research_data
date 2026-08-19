import matplotlib.pyplot as plt
import numpy as np
import os
# SPEC Workloads (41 items + Average)
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
        "whisper_trace_3",
        "Average"
]

data = [
52.9575,
62.5709,
59.1563,
0.0000,
7.9594,
7.0018,
0.0000,
0.0000,
0.0139,
0.0000,
0.0000,
0.1226,
0.3974,
0.0000,
0.0845,
10.2430,
2.0392,
61.6284,
77.1974,
0.0000,
5.3766,
82.7290,
67.2242,
0.0000,
0.0000,
0.0000,
19.1039
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
ax.set_ylabel('Percentage of prefetches filled \n in LLC', fontsize=5.0 * scale)
#ax.set_xlabel('SPEC Workload')  
ax.set_xticks(x_indices)
ax.set_xticklabels(workloads, rotation=45, ha='right')


# Baseline reference line at y = 1.0
#ax.axhline(y=1.0, color='black', linewidth=0.65, linestyle='--', zorder=5)

# Adjust limits (set y limit to 100 as requested)
ax.set_xlim(-1.0, len(workloads))
ax.set_ylim(0,10)

# Set y-axis ticks (major ticks every 10, minor ticks every 2)
from matplotlib.ticker import MultipleLocator
ax.yaxis.set_major_locator(MultipleLocator(2))
ax.yaxis.set_minor_locator(MultipleLocator(1))
ax.tick_params(which='minor', length=2, color='black')

# Annotate bars that exceed the y-limit of 100 using arrows with 90-degree rotated labels
ylim_max = 10
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
out_name = 'Bingo_Percentage_of_Prefetches_filled_at_LLC'
sample_dir = "../plots/bingo/"
os.makedirs(sample_dir, exist_ok=True)

plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.pdf'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print("Calculated Average: {:.4f}".format(avg_val))