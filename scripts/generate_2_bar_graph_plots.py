import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator
from collections import defaultdict

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

data_baseline = [
119.86,
138.03,
152.41,
112.80,
100.39,
133.79,
87.27,
86.39,
86.36,
87.00,
86.95,
87.19,
86.50,
86.51,
86.63,
90.59,
91.93,
124.37,
124.74,
99.48,
90.61,
123.58,
126.44,
118.54,
108.07,
115.89

]

data_prefetcher = [
 165.79,
188.74,
190.23,
230.26,
126.47,
287.13,
112.15,
102.46,
113.31,
94.06,
97.12,
110.62,
95.18,
107.11,
97.49,
132.77,
123.94,
161.71,
176.73,
133.28,
121.17,
167.72,
127.13,
135.59,
140.07,
137.43


]

# Calculate averages
avg_baseline   = np.mean(data_baseline)
avg_prefetcher = np.mean(data_prefetcher)

plot_workloads  = workloads + ["Average"]
plot_baseline   = data_baseline   + [avg_baseline]
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

# Grouped bar setup — 2 bars
n = len(plot_workloads)
x = np.arange(n)
bar_width = 0.27

fig, ax = plt.subplots()

color_baseline   = '#8C9EBC'
color_prefetcher = '#394761'

bars1 = ax.bar(x - bar_width/2, plot_baseline,   bar_width, label='Baseline', color=color_baseline,   edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x + bar_width/2, plot_prefetcher, bar_width, label='Prefetcher', color=color_prefetcher, edgecolor='black', linewidth=0.5)

ax.set_ylabel('Average Load Miss \nlatency of LLC')
ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=45, ha='right')
ax.set_xlim(-1.0, n)

ax.set_ylim(60, 140)
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.yaxis.set_minor_locator(MultipleLocator(5))
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
            lw=0.5,
            shrinkA=0,
            shrinkB=1
        ),
        ha='center',
        va='bottom',
        fontsize=3.0 * scale,
        color='black',
        rotation=90,
        clip_on=False
    )
# ─────────────────────────────────────────────────────────────────────────────

ax.legend(
    loc='lower center', bbox_to_anchor=(0.45, 1.02), ncol=2,
    frameon=True, facecolor='white', edgecolor='black',
    framealpha=1.0, fancybox=False
)

out_name = "Bingo_Average-Load_Miss_Latency_LLC"
root_dir = "../plots/Pref/Miss_Latency"
os.makedirs(root_dir, exist_ok=True)

out_png = os.path.join(root_dir, f'{out_name}.png')
out_pdf = os.path.join(root_dir, f'{out_name}.pdf')

plt.savefig(out_png, bbox_inches='tight')
plt.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print(f"Average Baseline:   {avg_baseline:.4f}")
print(f"Average Prefetcher: {avg_prefetcher:.4f}")
