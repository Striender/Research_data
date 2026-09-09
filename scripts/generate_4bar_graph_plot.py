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
        "Geomean"
]

# L1d Coverag,e data (26 workloads, already ordered)
data_1 = [
    1.05328301,
1.084787602,
1.097980411,
1.141387183,
1.555821624,
1.15260201,
1.070154925,
1.548165581,
1.357471828,
1.245457464,
2.525097255,
1.019454921,
2.533663411,
1.228290451,
2.528899789,
1.076962181,
2.060162364,
2.190058186,
1.062732723,
2.183226396,
1.06572752,
1.53195375,
2.501406137,
1.790210367,
2.060817387,
1.062102718,
2.484304606,
1.548065019,
1.066893572,
2.484228846,
1.784023873,
1.962581554,
2.478245811,
1.599039167,
2.481158079,
1.241478249,
2.532654325,
1.921436931,
2.389787394,
2.547232222,
2.541291772,
1.00756324,
2.503566398,
1.307373262,
1.002083878,
1.039373469,
1.309963062,
1.052064978,
1.002510716,
1.116523837,
1.037125442,
2.540397337,
1.225329761,
2.176477273,
2.537811832,
1.041218742,
1.071122588,
1.040286199,
1.925541072,
1.043679334,
1.059334112,
2.498583856,
1.06225701,
2.055952659,
1.909639175,
2.567717584,
1.12594335,
1.110510067  ,
1.544005277    


]

data_2 = [
    1.034547479 ,
1.07750639,
1.056769148,
1.128655347,
1.498281338,
1.135964518,
1.045153923,
1.474264637,
1.33555681,
1.194169777,
2.524971646,
1.01011411,
2.532058265,
1.197430708,
2.527929481,
1.01748393,
2.031397928,
2.172580526,
1.001063738,
2.165443571,
1.00099447,
1.479551005,
2.498019028,
1.754813065,
2.044045921,
1.001087995,
2.482720159,
1.466574581,
1.001387198,
2.482305371,
1.715426513,
1.905119324,
2.46735921,
1.493076754,
2.47986469,
1.119989171,
2.531552937,
1.879274837,
2.38162549,
2.547073257,
2.541019677,
1.000984935,
2.452958732,
1.16040301,
1.000052178,
1.021716231,
1.234515112,
1.039265551,
1.000268663,
1.077936735,
1.023017473,
2.54016622,
1.119986519,
2.154428221,
2.537433861,
1.029516535,
1.049710167,
1.023467632,
1.910388137,
1.024287171,
1.127604547,
2.498548473,
1.035805047,
2.049213829,
1.895733449,
2.568008483,
1.116914285,
1.106526282,
1.511116008

]

data_3 = [1.001568261,
1.054867142,
1.055518409,
1.102970446,
1.410743198,
1.110618552,
1.011100967,
1.364937518,
1.301965315,
1.100280523,
2.524946525,
1.013551909,
2.524667932,
1.213274415,
2.526148323,
1.00093163,
2.032413516,
2.173446116,
1.000827568,
2.166093964,
1.000536001,
1.478783244,
2.499346212,
1.754696639,
2.044424058,
1.000672948,
2.482872005,
1.467770293,
1.000819075,
2.482755442,
1.716332632,
1.90479051,
2.468883013,
1.494137515,
2.480114918,
1.121194851,
2.531676886,
1.879521048,
2.381573887,
2.546423153,
2.541148915,
1.002166426,
2.438318937,
1.108223426,
1.001193994,
1.025498601,
1.209321246,
1.020516453,
1.001577734,
1.084835951,
1.010374629,
2.540227394,
1.094256854,
2.162164839,
2.537718986,
1.030920657,
1.041590328,
1.020047902,
1.916190302,
1.019584856,
1.007800248,
2.497300598,
1.007267122,
2.035778688,
1.823381519,
2.567711767,
1.035346052,
1.102511862,
1.494225759
]

data_4 = [
    1.005731288,
1.056561212,
1.05125223,
1.105938604,
1.427610784,
1.113432777,
1.014978706,
1.384588811,
1.307267388,
1.122654039,
2.524984206,
1.009912612,
2.52529213,
1.19127737,
2.526066563,
1.000293439,
2.031388025,
2.173002137,
1.000082695,
2.165493164,
1.000053203,
1.478176554,
2.498682444,
1.754103831,
2.043968239,
1.000092215,
2.482423752,
1.466493758,
1.000052764,
2.482229104,
1.714234798,
1.903962574,
2.467280567,
1.492947678,
2.479795191,
1.11980925,
2.53145087,
1.878952036,
2.381509387,
2.546596481,
2.540985669,
1.000902783,
2.446898299,
1.079105105,
1.000037269,
1.016956722,
1.205870236,
1.020312441,
1.000254137,
1.056936117,
1.010468973,
2.54016622,
1.067745842,
2.151214235,
2.536413238,
1.028576051,
1.042124891,
1.019766468,
1.911393927,
1.019685311,
1.10570745,
2.497760196,
1.006774438,
2.042486401,
1.826327583,
2.567991027,
1.064267287,
1.102856785,
1.495420239
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

bars1 =ax.bar(x - 1.5*bar_width, plot_8k,  bar_width, label='No prefetcher',  color=color_8k,  edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x - 0.5*bar_width, plot_16k, bar_width, label='Berti', color=color_16k, edgecolor='black', linewidth=0.5)
bars3 = ax.bar(x + 0.5*bar_width, plot_32k, bar_width, label='Bingo', color=color_32k, edgecolor='black', linewidth=0.5)
bars4 = ax.bar(x + 1.5*bar_width, plot_64k, bar_width, label='Berti + Bingo', color=color_64k, edgecolor='black', linewidth=0.5)

# Axis labels
ax.set_ylabel('Speedup')

ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=90)

# Y-axis limits and ticks

ax.set_xlim(-1.0, n)
ax.set_ylim(0.8, 2.8)
ax.yaxis.set_major_locator(MultipleLocator(0.4))
ax.yaxis.set_minor_locator(MultipleLocator(0.1))
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
    bbox_to_anchor=(0.5, 1.02),
    ncol=4,
    title='Baseline',
    title_fontsize=4.0 * scale,
    frameon=True,
    facecolor='white',
    edgecolor='black',
    framealpha=1.0,
    fancybox=False
)

sample_dir = "../plots/all_AIML/pref/"
os.makedirs(sample_dir, exist_ok=True)

out_name = 'Ideal performance over perfetcher '
plt.savefig(os.path.join(sample_dir, f'{out_name}.png'), bbox_inches='tight')
plt.savefig(os.path.join(sample_dir, f'{out_name}.svg'), bbox_inches='tight')
plt.close()

print(f"Saved: {out_name}.png / .pdf")
print(f"Average  8KB: {avg_1:.4f}%")
print(f"Average 16KB: {avg_2:.4f}%")
print(f"Average 32KB: {avg_3:.4f}%")
print(f"Average 64KB: {avg_4:.4f}%")