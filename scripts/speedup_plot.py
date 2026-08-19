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

# Normalized IPC data (26 workloads + Geomean as last value)
data_gaze = [
    0.999968672, 1.002159827, 1.001356191, 1.014104913, 1.000064671, 1.001989596,
    1.07021177,  1.00045425,  1.106872616, 1.000403375, 1.022505511, 1.003397136,
    1.039913408, 1.030245642, 1.004019372, 1.000116311, 1.000096373, 1.012883295,
    1.020487817, 0.998786802, 1.000077605, 0.999662861, 1.023847871, 0.99958811,
    1.000358061, 0.998473453,
    1.013248269  # Geomean
]

data_ipcp = [
    0.996671392, 1.000932436, 1.002107594, 1.017940047, 1.000067158, 1.001741523,
    1.070352439, 1.00048229,  1.107691553, 1.000386087, 1.022428663, 1.003386265,
    1.039576012, 1.030019308, 1.004025193, 1.000130495, 1.00009905,  1.015176487,
    1.033867881, 1.004218006, 1.000080281, 1.000206465, 1.018331729, 1.00743118,
    1.000339855, 1.008670446,
    1.014567857  # Geomean
]

data_berti = [
    0.999780703, 1.004785873, 1.004126788, 1.041124274, 1.000049747, 1.000821899,
    1.070979218, 1.000504722, 1.108475432, 1.000443712, 1.022430859, 1.003429749,
    1.039990947, 1.030174046, 1.004418108, 1.000062411, 1.000085665, 1.016038322,
    1.033214785, 1.011926775, 1.000066901, 1.000222146, 1.018656652, 0.937186792,
    1.000060688, 1.022786721,
    1.013879723  # Geomean
]

data_sms = [
    0.996381607, 1.003035176, 1.000888316, 1.020089745, 1.000062183, 1.000872014,
    1.067861346, 1.000330873, 1.103873121, 1.000314056, 1.022099314, 1.003326476,
    1.034500391, 1.026183174, 1.003673025, 1.000215601, 1.000021416, 1.008086576,
    1.010763799, 1.006394095, 1.000034788, 1.000062724, 1.017658133, 1.007619963,
    1.000084964, 1.009845373,
    1.01297976   # Geomean
]

data_bingo = [
    1.036810489, 1.026174822, 1.028952197, 1.101536222, 0.999977614, 1.003162305,
    0.883139453, 1.250953364, 0.483635293, 1.731692559, 0.783365244, 2.145840411,
    0.727611839, 1.075302318, 1.074615962, 1.000317728, 0.999799223, 1.013161585,
    1.029394496, 1.026039787, 0.999716341, 1.000099312, 1.026795931, 1.050310634,
    0.999981794, 1.05132801,
    1.025389308  # Geomean
]

plot_workloads = workloads + ["Geomean"]

all_data   = [data_gaze, data_ipcp, data_berti, data_sms, data_bingo]
all_labels = ['Gaze (L1D)', 'IPCP (L1D)', 'Berti (L1D)', 'SMS (L2)', 'Bingo (L2)']

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

# Grouped bar setup — 5 bars
n = len(plot_workloads)
x = np.arange(n)
bar_width = 0.16   # 5 × 0.16 = 0.80 total group width

colors = ['#C5D3E8', '#8C9EBC', '#52688F', '#394761', '#262f40']

fig, ax = plt.subplots()

Y_MAX = 1.2
Y_MIN = min(min(d) for d in all_data)

# Track annotation x-positions to stagger overlapping labels vertically
annotation_offsets = {}   # key: round(x_pos,3) -> next y offset to use

for i, (d, c, lbl) in enumerate(zip(all_data, colors, all_labels)):
    offset = (-2 + i) * bar_width
    # Cap bar heights at Y_MAX for display
    capped = [min(v, Y_MAX) for v in d]
    ax.bar(x + offset, capped, bar_width, label=lbl, color=c, edgecolor='black', linewidth=0.5)
    # Annotate bars that exceed Y_MAX with actual value
    for j, (actual, cap) in enumerate(zip(d, capped)):
        if actual > Y_MAX:
            x_pos = round(float(x[j] + offset), 3)
            # Each overlapping annotation at same group is staggered by bar_width
            y_base = Y_MAX + 0.005
            stagger = annotation_offsets.get(x_pos, 0)
            annotation_offsets[x_pos] = stagger + bar_width * 0.6
            ax.text(
                x_pos, y_base + stagger,
                f'{actual:.2f}',
                ha='center', va='bottom',
                fontsize=3.0 * scale,
                rotation=90,
                color='black',
                clip_on=False
            )

# Baseline reference line at y=1 (dashed)
ax.axhline(y=1.0, color='black', linewidth=0.75, linestyle='--', zorder=5)

ax.set_ylabel('Normalized IPC')
ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=45, ha='right')
ax.set_xlim(-1.0, n)

ax.set_ylim(max(0, Y_MIN * 0.95), Y_MAX)
ax.yaxis.set_major_locator(MultipleLocator(0.1))
ax.yaxis.set_minor_locator(MultipleLocator(0.05))
ax.tick_params(which='minor', length=2, color='black')

ax.legend(
    loc='lower center', bbox_to_anchor=(0.5, 1.1), ncol=5,
    frameon=True, facecolor='white', edgecolor='black',
    framealpha=1.0, fancybox=False
)

sample_dir = "../plots/speedup/"
os.makedirs(sample_dir, exist_ok=True)

out_name = 'speedup_normalized_ipc'
plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.pdf'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print("Geomean values:")
for lbl, d in zip(all_labels, all_data):
    print(f"  {lbl}: {d[-1]:.6f}")
