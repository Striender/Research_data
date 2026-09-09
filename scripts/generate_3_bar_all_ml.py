import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator
from collections import defaultdict

# Workload list (68 workloads)
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
]

# L1D data (2KB)
data_l1d = [
     11.5807,  61.3493,   9.79898, 69.9765,  50.823,
     54.8254,  11.7619,  54.5602,  53.499,   51.4955,
     10.3916,   6.47672, 10.8022,  20.7677,  10.1756,
     35.5561,  49.6716,  35.5557,  44.4579,  35.5557,
     44.5316,  49.7096,  36.7578,  42.3869,  49.7083,
     44.4492,  47.1833,  35.5572,  49.7096,  48.5096,
     35.0017,  35.0048,  35.0038,  33.8277,  33.375,
     33.358,   34.7086,  34.6713,  34.7145,
    247.993,  127.808,    0.93589, 91.1947, 333.285,
      0.936245,141.049, 233.249,  127.771,    0.936235,
    170.021,  132.968,  127.808,  329.787,   90.8813,
     48.2994,   8.15594, 26.6895,   7.22027,  6.95219,
      7.15322,  18.591,  17.8415,  17.3496,  45.5783,
     76.7686,  101.179,  42.6622,  18.5104,
]

# L2 data (4KB)
data_l2 = [
      5.97896,  7.05802,  2.57074,  7.1707,  24.7294,
      7.00565,  5.38332, 30.0331,  28.6555,  26.0624,
      3.64559,  2.22222,  4.53835,  3.13804,  4.14396,
     35.5533,  35.5571,  35.552,   35.5837,  35.5511,
     35.5839,  35.5988,  35.5555,  35.5717,  35.5975,
     35.5837,  35.6221,  35.5544,  35.5989,  35.5925,
     34.9858,  34.9902,  34.9886,  33.6919,  33.0233,
     32.9918,  34.6802,  34.6308,  34.6655,
     15.9812,   7.86426,  0.12493,  7.03593,  8.49687,
      0.03786,  8.55786, 18.0569,   7.82776,  0.038895,
     10.4054,   9.00589,  7.81373,  5.62727,  5.21031,
      4.46024,  3.07107,  4.20177,  3.67452,  2.59463,
      3.58921,  6.5955,   6.59238,  6.59868, 15.8719,
     17.3,      1.11971, 15.2546,   6.49913,
]

# LLC data (8KB)
data_llc = [
      2.25672,  2.39162,  2.44913,  3.77224, 23.4112,
      3.36481,  3.66739, 29.6188,  27.7568,  24.7368,
      2.89183,  0.587705, 3.6835,   2.83553,  1.28089,
     35.5514,  35.5526,  35.5503,  35.582,   35.549,
     35.5805,  35.5956,  35.5534,  35.5685,  35.5942,
     35.5824,  35.6209,  35.5524,  35.5956,  35.5894,
     34.9608,  34.9634,  34.9047,  32.0008,  31.3332,
     31.2982,  34.2008,  34.1441,  34.0834,
     12.9889,   7.41171,  0.05488,  6.38687,  8.4622,
      0.005935, 2.16559, 12.2804,   7.36604,  0.005325,
      6.39865,  8.02549,  7.38212,  5.55604,  4.7336,
      2.23513,  1.12663,  3.16886,  2.08378,  0.67407,
      2.47245,  5.10283,  5.10277,  5.15609, 15.6634,
     17.2996,   1.11852, 15.0212,   0.725355,
]

assert len(data_l1d) == len(workloads), f"L1D length mismatch: {len(data_l1d)}"
assert len(data_l2)  == len(workloads), f"L2 length mismatch: {len(data_l2)}"
assert len(data_llc) == len(workloads), f"LLC length mismatch: {len(data_llc)}"

# Calculate averages and append
avg_l1d = np.mean(data_l1d)
avg_l2  = np.mean(data_l2)
avg_llc = np.mean(data_llc)

plot_workloads = workloads + ["Average"]
plot_l1d = data_l1d + [avg_l1d]
plot_l2  = data_l2  + [avg_l2]
plot_llc = data_llc + [avg_llc]

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
    'xtick.labelsize': 3.0 * scale,
    'ytick.labelsize': 4.0 * scale,
    'text.usetex': False,
    'font.family': 'serif',
   # 'font.serif': ['Times', 'Times New Roman', 'Liberation Serif'],
    'patch.linewidth': 0.5,
    'patch.edgecolor': 'black',
    'figure.figsize': [fig_width, fig_width * golden_mean * 0.85],
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

# Grouped bar setup — 3 bars
n = len(plot_workloads)
x = np.arange(n)
bar_width = 0.27

fig, ax = plt.subplots()

color_l1d = '#8C9EBC'
color_l2  = "#D8EF84"
color_llc = "#f88243"

bars1 = ax.bar(x - bar_width, plot_l1d, bar_width, label='L1D',
               color=color_l1d, edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x,              plot_l2,  bar_width, label='L2',
               color=color_l2,  edgecolor='black', linewidth=0.5)
bars3 = ax.bar(x + bar_width,  plot_llc, bar_width, label='LLC',
               color=color_llc, edgecolor='black', linewidth=0.5)

ax.set_ylabel('MPKI')   # ← update ylabel as needed
ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=90)
ax.set_xlim(-1.0, n)

# Y-axis: set ylim to cap outliers, annotate exceeding bars
Y_MAX = 60
ax.set_ylim(0, Y_MAX)
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.yaxis.set_minor_locator(MultipleLocator(5))
ax.tick_params(which='minor', length=2, color='black')

# ── Collision-safe annotations for bars exceeding Y_MAX ──────────────────────
ylim_max = ax.get_ylim()[1]
overflow_bars = []
for rect in list(bars1) + list(bars2) + list(bars3):
    height = rect.get_height()
    if height > ylim_max:
        bar_x = rect.get_x() + rect.get_width() / 2.0
        overflow_bars.append((bar_x, height))

overflow_bars.sort(key=lambda t: t[0])
stagger_count = defaultdict(int)
text_step_pts = 14

for bar_x, height in overflow_bars:
    group_key = round(bar_x)
    level = stagger_count[group_key]
    stagger_count[group_key] += 1
    y_offset = 8 + level * text_step_pts

    ax.annotate(
        f'{height:.1f}',
        xy=(bar_x, ylim_max),
        xytext=(0, y_offset),
        textcoords='offset points',
        arrowprops=dict(arrowstyle="->", color='black', lw=0.5, shrinkA=0, shrinkB=1),
        ha='center', va='bottom',
        fontsize=3.0 * scale,
        color='black',
        rotation=90,
        clip_on=False
    )
# ─────────────────────────────────────────────────────────────────────────────

ax.legend(
    loc='lower center', bbox_to_anchor=(0.35, 1.02), ncol=3,
    frameon=True, facecolor='white', edgecolor='black',
    framealpha=1.0, fancybox=False
)

out_name = 'l1d_l2_llc_grouped_bar'
sample_dir = "../plots/sample"
os.makedirs(sample_dir, exist_ok=True)

plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.svg'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.pdf'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.svg / .pdf")
print(f"Average L1D: {avg_l1d:.4f}")
print(f"Average L2:  {avg_l2:.4f}")
print(f"Average LLC: {avg_llc:.4f}")