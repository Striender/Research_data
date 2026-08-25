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
0.051415,
0.33053,
2.31538,
0.312035,
0,
2.58726,
0.00001,
0.002535,
0.009925,
0.00039,
0.0028,
0.001415,
0.00017,
0.000525,
0,
0.024225,
0.00625,
0.09058,
0.208815,
0.106435,
0.004695,
0.847705,
0.0185,
0.03358,
0.00337,
0.048445,
0.269499615
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
ax.set_ylabel('# of MSHR Full events per \n kilo instruction', fontsize=5.0 * scale)
#ax.set_xlabel('SPEC Workload')  
ax.set_xticks(x_indices)
ax.set_xticklabels(workloads, rotation=45, ha='right')


# Baseline reference line at y = 1.0
#ax.axhline(y=1.0, color='black', linewidth=0.65, linestyle='--', zorder=5)

# Adjust limits (set y limit to 100 as requested)
ylim_max = 0.2
ax.set_xlim(-1.0, len(workloads))
ax.set_ylim(0,ylim_max)

# Set y-axis ticks (major ticks every 10, minor ticks every 2)
from matplotlib.ticker import MultipleLocator
ax.yaxis.set_major_locator(MultipleLocator(0.05))
ax.yaxis.set_minor_locator(MultipleLocator(0.025))
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
out_name = 'Bingo_MSHR_FULL'
sample_dir = "../plots/Pref/"
os.makedirs(sample_dir, exist_ok=True)

plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.pdf'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print("Calculated Average: {:.4f}".format(avg_val))