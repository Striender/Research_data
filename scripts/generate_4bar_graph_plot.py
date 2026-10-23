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
        "whisper_trace_8",
            "Geomean"
]

# L1d Coverag,e data (26 workloads, already ordered)
data_1 = [
   1.023073447,
1.006080411,
1.065147357,
1.035992872,
1.061251926,
1.034652575,
1.012814186,
1.059713016,
1.064662738,
1.056942898,
1.004703169,
1.04690247,
1.007433971,
1.051550273,
1.002189002,
1.031904935,
1.0401583,
1.02732887,
1.027448758,
1.046550072,
1.04034467,
1.030882274,
1.027429041,
1.036441194,
1.039336169,
1.027211429,
1.038657317,
1.028384046,
1.031304464,
1.039712058,
1.048539277,
1.055621686,
1.056398883,
1.042746743,
1.041168671,
1.043189094,
1.034625745,
1.034013095,
1.034872355,
1.011730481,
1.005300288,
1.263097856,
1.027021296,
0.8448100234,
1.265272435,
1.055861036,
0.8779276953,
1.006077082,
1.23528085,
0.9259106586,
1.004645784,
1.00329712,
0.8300736196,
1.00695181,
1.004856564,
1.076000076,
1.004208964,
1.004757956,
1.094859387,
1.004635958,
1.006746864,
1.008595253,
1.009860714,
1.055240056,
1.137295255,
1.001744397,
1.071538302,
0.9978834069,
1.031400962

]

data_2 = [
    1.023794987,
1.006635658,
1.176930344,
1.037022463,
1.066699864,
1.035448097,
1.013485637,
1.064964673,
1.068956463,
1.064860936,
1.004881373,
1.056575717,
1.007656006,
1.080408997,
1.002971437,
1.032194862,
1.040233141,
1.027364324,
1.027468345,
1.046556539,
1.040365293,
1.030909764,
1.027447423,
1.03648533,
1.039431355,
1.027229791,
1.03870111,
1.028414373,
1.031342351,
1.039928866,
1.049114021,
1.057249979,
1.057071846,
1.043632666,
1.042713354,
1.044010421,
1.035206087,
1.034768824,
1.035377542,
1.011730481,
1.005306814,
1.288704436,
1.027117398,
0.8449428106,
1.295111476,
1.056482057,
0.8934108527,
1.006114085,
1.268851863,
0.9281578264,
1.004691594,
1.003298205,
0.830105894,
1.007048229,
1.00525802,
1.090335934,
1.004302658,
1.00486654,
1.114939907,
1.004774641,
1.011901194,
1.011725465,
1.012649863,
1.057773144,
1.140469288,
1.00230225,
1.075755241,
1.001517712,
1.036245173

]

data_3 = [1.023787058,
1.009202538,
1.195451923,
1.03819477,
1.065742031,
1.035798506,
1.013663611,
1.066686576,
1.070624581,
1.065656227,
1.005777456,
1.061377489,
1.008257175,
1.114224185,
1.003823444,
1.032214364,
1.040246044,
1.027363011,
1.027476179,
1.046557833,
1.040365293,
1.030905837,
1.027447423,
1.036497014,
1.039441645,
1.027238972,
1.038703686,
1.028418328,
1.031334513,
1.039983068,
1.049263404,
1.057485503,
1.057287246,
1.044,
1.042998135,
1.044243449,
1.035720631,
1.035233585,
1.035943245,
1.011730481,
1.005310077,
1.30288862,
1.028797089,
0.8449009735,
1.305067782,
1.056769666,
0.9027852152,
1.006116261,
1.281701106,
1.12840128,
1.004737404,
1.003299289,
0.8301415657,
1.008590933,
1.005335142,
1.099769176,
1.005082404,
1.007571271,
1.128237674,
1.007508668,
1.012175179,
1.012426769,
1.012872995,
1.061906644,
1.164269038,
1.003046054,
1.081044023,
1.001493101,
1.041739293
]

data_4 = [
   1.024032858,
1.010012652,
1.208138986,
1.03953018,
1.066080588,
1.036300442,
1.013566534,
1.068230752,
1.07196307,
1.069279689,
1.006757578,
1.063151047,
1.008969361,
1.13692082,
1.004165255,
1.032218264,
1.040243463,
1.027376142,
1.027482708,
1.046541017,
1.040366582,
1.030905837,
1.027450048,
1.036500908,
1.039448077,
1.027242907,
1.038729446,
1.02841701,
1.031335819,
1.039984359,
1.04926467,
1.05753388,
1.057380288,
1.044082618,
1.043159596,
1.044203974,
1.03613516,
1.035700979,
1.036285299,
1.011729319,
1.006675122,
1.305012496,
1.029361164,
0.8449137065,
1.307263696,
1.056874057,
0.9086772618,
1.006879161,
1.284051222,
1.310813413,
1.004749694,
1.004684925,
0.8303929662,
1.009410494,
1.00548199,
1.104032735,
1.005074076,
1.007561399,
1.133761057,
1.007538385,
1.012183741,
1.012076117,
1.012881577,
1.063578137,
1.168108298,
1.00320544,
1.082772836,
1.001993535,
1.045231532
]

# Calculate averages
avg_1  = np.mean(data_1)
avg_2 = np.mean(data_2)
avg_3 = np.mean(data_3)
avg_4 = np.mean(data_4)

# Append average
plot_workloads = workloads# + ["Average"]
plot_8k  = data_1  #+ [avg_1]
plot_16k = data_2 #+ [avg_2]
plot_32k = data_3 #+ [avg_3]
plot_64k = data_4 #+ [avg_4]

# Figure parameters — exact Thesis.ipynb style
scale = 1.5
x_spacing = 1.45
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
    'xtick.labelsize': 3.0 * scale,
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

# Grouped bar setup — 4 bars, slightly narrower width
n = len(plot_workloads)
x = np.arange(n)
bar_width = 0.20

fig, ax = plt.subplots()

# Colors from palette (light → dark)
color_8k  = '#C5D3E8'
color_16k = '#8C9EBC'
color_32k = '#52688F'
color_64k = '#262f40'

bars1 =ax.bar(x - 1.5*bar_width, plot_8k,  bar_width, label='2KB',  color=color_8k,  edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x - 0.5*bar_width, plot_16k, bar_width, label='4KB', color=color_16k, edgecolor='black', linewidth=0.5)
bars3 = ax.bar(x + 0.5*bar_width, plot_32k, bar_width, label='8KB', color=color_32k, edgecolor='black', linewidth=0.5)
bars4 = ax.bar(x + 1.5*bar_width, plot_64k, bar_width, label='16KB', color=color_64k, edgecolor='black', linewidth=0.5)

# Axis labels
ax.set_ylabel('Speedup')

ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=90)

# Y-axis limits and ticks

ax.set_xlim(-1.0, n)
ax.set_ylim(0.8, 1.3)
ax.yaxis.set_major_locator(MultipleLocator(0.1))
ax.yaxis.set_minor_locator(MultipleLocator(0.05))
ax.tick_params(which='minor', length=2, color='black')
ax.axhline(y=1.0, color='black', linewidth=0.65, linestyle='--', zorder=5)
# ── Collision-safe annotations for bars exceeding ylim ───────────────────────
ylim_max = ax.get_ylim()[1]

# Collect all bars that exceed the y limit
overflow_bars = []
for rect in list(bars1) + list(bars2) + list(bars3) + list(bars4):
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
    bbox_to_anchor=(0.32, 1.02),
    ncol=4,
    title='L1D Cache Size',
    title_fontsize=4.0 * scale,
    frameon=True,
    facecolor='white',
    edgecolor='black',
    framealpha=1.0,
    fancybox=False
)

sample_dir = "../plots/cache_sensitivity/"
os.makedirs(sample_dir, exist_ok=True)

out_name = 'SPeedup_of_2K_4K_8K_16K'
plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
#plt.savefig(os.path.join(sample_dir, f'{out_name}.svg'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print(f"Average  8KB: {avg_1:.4f}%")
print(f"Average 16KB: {avg_2:.4f}%")
print(f"Average 32KB: {avg_3:.4f}%")
print(f"Average 64KB: {avg_4:.4f}%")