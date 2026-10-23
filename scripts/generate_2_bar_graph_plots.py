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

data_baseline = [
0.123  ,
0.2241,
0.3186,
0.2896,
20.9426,
0.2927,
0.1355,
18.6554,
19.506,
20.3263,
0.0736,
0.0962,
0.0959,
5.5438,
0.1127,
0.5559,
0.5561,
0.556,
0.5561,
0.556,
0.5561,
0.5564,
0.5561,
0.5562,
0.5564,
0.5561,
0.5567,
0.5561,
0.5564,
0.5563,
0.5501,
0.5504,
0.5498,
0.5358,
0.5254,
0.525,
0.5466,
0.5471,
0.5466,
2.098,
0.4715,
0.2077,
0.2379,
2.7592,
0.2258,
1.0675,
0.9216,
0.4694,
0.1879,
0.4715,
2.1204,
0.4755,
4.0505,
1.6906,
0.1421,
0.6746,
0.1244,
0.0616,
0.061,
0.1832,
0.1302,
0.135,
0.1288,
0.5002,
0.604,
0.1999,
0.5082,
0.1518

]

data_prefetcher = [ 
0.0043  ,
0.0122,
0.0578,
0.0235,
0.3947,
0.0156,
0.0108,
0.4978,
0.4618,
0.4143,
0.0588,
0.013,
0.0714,
0.1008,
0.016,
0.5559,
0.556,
0.5559,
0.5561,
0.5559,
0.5561,
0.5564,
0.556,
0.5562,
0.5564,
0.5561,
0.5567,
0.5562,
0.5564,
0.5563,
0.5497,
0.5499,
0.5496,
0.5288,
0.5184,
0.5181,
0.545,
0.5452,
0.545,
0.128,
0.1182,
0.0066,
0.116,
0.1234,
0.0058,
0.0254,
0.2472,
0.1182,
0.0057,
0.1363,
0.1214,
0.1182,
0.0781,
0.087,
0.0125,
0.0054,
0.0553,
0.0332,
0.0032,
0.0584,
0.1062,
0.1061,
0.1062,
0.2982,
0.3812,
0.0189,
0.2769,
0.0037
]

# Calcula,te averages
avg_baseline   = np.mean(data_baseline)
avg_prefetcher = np.mean(data_prefetcher)

plot_workloads  = workloads + ["Average"]
plot_baseline   = data_baseline  + [avg_baseline]
plot_prefetcher = data_prefetcher + [avg_prefetcher]

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

bars1 = ax.bar(x - bar_width/2, plot_baseline,   bar_width, label='DTLB', color=color_baseline,   edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x + bar_width/2, plot_prefetcher, bar_width, label='STLB', color=color_prefetcher, edgecolor='black', linewidth=0.5)

ax.set_ylabel('MPKI', fontsize=3 * scale)
ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=90)
ax.set_xlim(-1.0, n)

#ax.axhline(y=1.0, color='black', linewidth=0.65, linestyle='--', zorder=5)


ax.set_ylim(0,1)
ax.yaxis.set_major_locator(MultipleLocator(0.2))
ax.yaxis.set_minor_locator(MultipleLocator(0.1))
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
        fontsize=2 * scale,
        color='black',
        rotation=90,
        clip_on=False
    )
# ───────────────────────────────────────────────────────────────────────────

ax.legend(
    loc='lower center', bbox_to_anchor=(0.355, 1.02), ncol=2,
    frameon=True, facecolor='white', edgecolor='black', title_fontsize=3.0 * scale, framealpha=1.0, fancybox=False)
    

out_name = "TLB_MPKI_48KB"
root_dir = "../plots/cache_sensitivity/"
os.makedirs(root_dir, exist_ok=True)

out_png = os.path.join(root_dir, f'{out_name}.png')
out_svg = os.path.join(root_dir, f'{out_name}.svg')

plt.savefig(out_png, bbox_inches='tight')
#plt.savefig(out_svg, bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png ")
print(f"Average Baseline:   {avg_baseline:.4f}")
print(f"Average Prefetcher: {avg_prefetcher:.4f}")
