import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator
from collections import defaultdict

# AI/ML Workloads — final order: 15M → 42M → 110M
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
        #"Geomean"
        
    
]

data_baseline = [
4.495,
5.235,
5.889,
5.563,
5.660,
5.295,
5.398,
6.079,
5.883,
5.677,
4.610,
4.469,
5.486,
3.736,
5.711,
3.098,
3.161,
3.039,
3.063,
3.198,
3.156,
3.061,
3.048,
3.122,
3.162,
3.050,
3.147,
3.019,
3.074,
3.161,
3.134,
3.134,
3.134,
3.178,
3.175,
3.179,
2.948,
2.944,
2.947,
6.038,
6.664,
1.113,
5.918,
2.262,
1.018,
5.359,
5.585,
6.672,
1.017,
5.877,
6.367,
6.581,
2.267,
5.838,
4.364,
4.719,
4.597,
4.369,
4.391,
4.233,
6.382,
6.326,
6.073,
6.199,
8.415,
6.289,
6.102,
2.729


]

data_prefetcher = [
8.365   ,
8.299,
10.008,
10.907,
10.858,
10.282,
8.390,
11.653,
11.366,
11.002,
8.421,
8.077,
9.380,
6.437,
9.543,
6.521,
7.013,
7.392,
6.998,
7.618,
6.738,
7.428,
7.217,
7.480,
6.605,
6.961,
6.657,
7.053,
7.433,
6.684,
6.807,
6.827,
6.817,
6.501,
6.476,
6.497,
6.720,
6.728,
6.717,
11.156,
12.667,
2.132,
12.108,
9.328,
1.085,
9.654,
12.369,
12.814,
1.098,
11.935,
12.609,
12.689,
9.198,
11.524,
8.241,
8.067,
7.601,
8.156,
7.067,
8.208,
12.561,
12.539,
12.403,
12.070,
17.400,
11.206,
11.873 ,
5.432


]

# Calculate averages
avg_baseline   = np.mean(data_baseline)
avg_prefetcher = np.mean(data_prefetcher)

plot_workloads  = workloads + ["Average"]
plot_baseline   = data_baseline  + [avg_baseline]
plot_prefetcher = data_prefetcher+ [avg_prefetcher]

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
    'legend.fontsize': 3.0 * scale,
    'xtick.labelsize': 3.0 * scale,
    'ytick.labelsize': 3.0 * scale,
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

# Grouped bar setup — 2 bars
n = len(plot_workloads)
x = np.arange(n)
bar_width = 0.27

fig, ax = plt.subplots()

color_baseline   = '#8C9EBC'
color_prefetcher = '#394761'

bars1 = ax.bar(x - bar_width/2, plot_baseline,   bar_width, label='No prefetcher', color=color_baseline,   edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x + bar_width/2, plot_prefetcher, bar_width, label='Bingo (L1D) + Bingo (L2)', color=color_prefetcher, edgecolor='black', linewidth=0.5)

ax.set_ylabel('Average DRAM read \n queue occupancy', fontsize=3 * scale)
ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=90)
ax.set_xlim(-1.0, n)

#ax.axhline(y=1.0, color='black', linewidth=0.65, linestyle='--', zorder=5)


ax.set_ylim(0,12)
ax.yaxis.set_major_locator(MultipleLocator(2))
ax.yaxis.set_minor_locator(MultipleLocator(1))
ax.tick_params(which='minor', length=2, color='black')

# ── Collision-safe annotations for bars exceeding ylim ───────────────────────
ylim_max = ax.get_ylim()[1]

# Collect all bars that exceed the y limit
overflow_bars = []
for rect in list(bars1) + list(bars2):
    height = rect.get_height()
    if height > ylim_max:
        bar_x = rect.get_x() + rect.get_width() / 2.0
        overflow_bars.append((bar_x, height))

# Sort left-to-right so stacking order is consistent within each group
overflow_bars.sort(key=lambda t: t[0])

# Track stagger level per x-group (identified by rounded bar_x)
stagger_count = defaultdict(int)
text_step_pts = 12   # vertical gap in points between stacked labels

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
            lw=0.4,
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
# ───────────────────────────────────────────────────────────────────────────

ax.legend(
    loc='lower center', bbox_to_anchor=(0.35, 1.02), ncol=2,
    frameon=True, facecolor='white', edgecolor='black', title_fontsize=3.0 * scale, framealpha=1.0, fancybox=False)
    

out_name = "Bingo+bingo_DRAM_RQ"
root_dir = "../plots/aiml_bingo/"
os.makedirs(root_dir, exist_ok=True)

out_png = os.path.join(root_dir, f'{out_name}.png')
out_svg = os.path.join(root_dir, f'{out_name}.svg')

plt.savefig(out_png, bbox_inches='tight')
#plt.savefig(out_svg, bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png ")
print(f"Average Baseline:   {avg_baseline:.4f}")
print(f"Average Prefetcher: {avg_prefetcher:.4f}")
