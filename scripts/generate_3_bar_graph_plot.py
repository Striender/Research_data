from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator

# AI/ML Workloads (26 items)
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
    "whisper_trace_8"
    #"Geomean"

    
]

# 2KB data
data_2kb = [ 
 1.017562778 ,
1.006881423,
1.045923008,
1.029020196,
1.041711572,
1.024329725,
1.01782984,
1.033227475,
1.035995091,
1.037207102,
1.024612406,
1.009487372,
1.033200462,
1.033791449,
1.007819306,
1.076499038,
1.091498781,
1.058883393,
1.06169409,
1.102540024,
1.097010241,
1.066456255,
1.060405337,
1.081333235,
1.094280235,
1.062360562,
1.095800285,
1.065457221,
1.068007285,
1.092201611,
1.135224334,
1.124540889,
1.126341146,
1.116277089,
1.111210841,
1.118348839,
1.116665811,
1.115318532,
1.11657315,
1.006130812,
1.00229284,
1.006259053,
1.095016395,
1.202089306,
1.001927027,
1.014240884,
1.082198592,
1.001136188,
1.002110012,
1.033073037,
0.9984569919,
0.9990480527,
1.151653978,
1.005274119,
1.014494683,
1.011684249,
1.026187603,
1.019732686,
1.02816231,
1.023655275,
1.004469369,
1.006363053,
1.006076054,
1.024859156,
1.005684671,
1.001469898,
1.030879835,
0.9998851461,
1.049841929



]
# 4KB data,,
data_4kb = [
1.023877922  ,
1.016983627,
1.046896462,
1.033817071,
0.9767627838,
1.027356058,
1.019081897,
0.9866428888,
0.9878900673,
0.9829694827,
1.024209564,
1.011384697,
1.035173002,
1.035798818,
1.008837349,
1.076551521,
1.0913988,
1.058898691,
1.061724091,
1.102294213,
1.097059032,
1.066340121,
1.06041273,
1.081129281,
1.09431176,
1.062437696,
1.095762055,
1.065422767,
1.068035273,
1.092956542,
1.135220373,
1.124634086,
1.126429807,
1.116286873,
1.111171995,
1.11834743,
1.116629513,
1.115302327,
1.116556507,
0.9903137804,
0.990783131,
1.009239844,
1.08919856,
1.199190314,
1.005408329,
1.006889806,
1.086863328,
0.9904836128,
1.005966806,
1.049809027,
0.987381067,
0.9891064547,
1.11529718,
1.089722562,
1.019365408,
1.010841867,
1.029909479,
1.020317341,
1.025731157,
1.024399905,
1.008730179,
1.008683595,
1.006662092,
1.094919469,
1.004998203,
1.002379114,
1.08681547,
1.020048932,
1.049511576

]
# 8KB data,
data_8kb = [
    0.341124,
0.345253,
0.53567,
0.573194,
1.88564,
0.531205,
0.544727,
2.53769,
2.17813,
1.89253,
0.339265,
0.107995,
0.517682,
0.219643,
0.213301,
2.33134,
2.35088,
2.31033,
2.32293,
2.34578,
2.35239,
2.31696,
2.30892,
2.33615,
2.35637,
2.31138,
2.35351,
2.29937,
2.32255,
2.34981,
2.16942,
2.10095,
2.09553,
2.30184,
2.29768,
2.29284,
2.26911,
2.26726,
2.26457,
1.09348,
0.693826,
0.0117765,
0.840927,
0.412697,
0.00128875,
0.25091,
1.06335,
0.696706,
0.00121556,
0.61393,
0.715697,
0.671564,
0.284449,
0.552789,
0.310285,
0.136566,
0.38639,
0.254672,
0.139805,
0.283677,
0.690117,
0.687658,
0.682423,
1.35471,
2.29386,
0.14187,
1.28554,
0.0628811

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
ax.set_ylabel('Average load occupancy \n in MSHR', fontsize=3.5 * scale)

ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=90)

# Y-axis limits and ticks
ax.set_xlim(-x_spacing, x[-1] + x_spacing)
ax.set_ylim(0,4)
ax.yaxis.set_major_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator( 0.5))
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

    y_offset = 6 + level * text_step_pts  # 1st: 8pt, 2nd: 22pt, 3rd: 36pt …

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
        fontsize=2.5 * scale,
        color='black',
        rotation=90,
        clip_on=False
    )


# Legend
ax.legend(
    loc='lower center',
    bbox_to_anchor=(0.42, 1.02),
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

out_png = os.path.join(root_dir, 'baseline_Average_load_occupancy_l1+l2+llc.png')
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
