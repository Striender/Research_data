import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator

# AI/ML Workloads (26 items)
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
    "stable-diffusion.1",
    "stable-diffusion.2",
    "stable-diffusion.v1-5",
    "stable-diffusion.v2-1_768.1",
    "stable-diffusion.v2-1_768.2",
    "stable-diffusion.v2-1_768.3",
    "vit.cpp-base-f16",
    "vit.cpp-large-f16",
    "whisper_trace_1",
    "whisper_trace_2",
    "whisper_trace_3"
]

# 2KB data
data_2kb = [
   90.8198300602894,
66.217504518292,
60.468702971186,
4.12001937493709,
91.0705339590399,
90.1239592797712,
65.8956866410951,
67.8976899834535,
74.5846244638381,
63.1844830391105,
74.1907105404649,
59.2965410714425,
74.6020086764291,
67.7123035872768,
73.1022298248797,
71.8092485831166,
72.0454555320292,
34.7528557088387,
15.0491396089103,
71.4655718259983,
72.0241626685242,
81.6209303943898,
84.813946944878,
85.0853342865563,
88.4005220156653,
86.111495115683

]

# 4KB data
data_4kb = [89.3584787129142,
47.8796485986215,
38.6358149118004,
5.03199778071028,
88.8534861658445,
88.5480525134498,
84.2177483728268,
85.5659351292908,
89.8886771282515,
82.6806883325647,
88.8146526224983,
79.47733058251,
89.8801399186165,
85.3221077863505,
88.7224943628023,
46.4025167138635,
86.917127853219,
32.0161016747408,
3.10695604135704,
84.874992611256,
86.8075623782207,
36.7291469729773,
87.1929186823884,
84.2264964787721,
87.880509476889,
85.423501911193

]

# 8KB data
data_8kb = [
    89.3090047898513,
46.3076783670185,
37.4994243149814,
5.44154715751919,
88.3669566620516,
88.1291544014026,
91.5004162569331,
92.2041601293444,
94.5947621234869,
90.8024670653338,
93.5146464820437,
88.7535221946967,
94.5728894502072,
92.0948499822298,
93.8636618890876,
49.171993525791,
15.4372582042529,
35.7480992170713,
1.54219374753271,
88.5118111498601,
16.263405088876,
33.2961391377233,
62.8728175888132,
83.0318880824827,
87.4192597390532,
84.1439795144101

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
    'font.serif': ['Times', 'Times New Roman', 'Liberation Serif'],
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

# Grouped bar setup
n = len(plot_workloads)
x = np.arange(n)

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
    label='1KB',
    color=color_2kb,
    edgecolor='black',
    linewidth=0.5
)

bars2 = ax.bar(
    x,
    plot_4kb,
    bar_width,
    label='2KB',
    color=color_4kb,
    edgecolor='black',
    linewidth=0.5
)

bars3 = ax.bar(
    x + bar_width,
    plot_8kb,
    bar_width,
    label='4KB',
    color=color_8kb,
    edgecolor='black',
    linewidth=0.5
)

# Axis labels
ax.set_ylabel('L1D Coverage (%)')

ax.set_xticks(x)
ax.set_xticklabels(plot_workloads, rotation=45, ha='right')

# Y-axis limits and ticks
ax.set_xlim(-1.0, n)
ax.set_ylim(0, 100)
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.yaxis.set_minor_locator(MultipleLocator(5))
ax.tick_params(which='minor', length=2, color='black')

# Legend
ax.legend(
    loc='lower center',
    bbox_to_anchor=(0.5, 1.02),
    ncol=3,
    title='Region size',
    title_fontsize=4.0 * scale,
    frameon=True,
    facecolor='white',
    edgecolor='black',
    framealpha=1.0,
    fancybox=False
)

root_dir = "../plots/"
os.makedirs(root_dir, exist_ok=True)

out_png = os.path.join(root_dir, 'GAZE_Region_Coverage_2kb_4kb_8kb.png')
out_pdf = os.path.join(root_dir, 'GAZE_Region_Coverage_2kb_4kb_8kb.pdf')

plt.savefig(out_png, bbox_inches='tight')
plt.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Saved: {out_png}")
print(f"Saved: {out_pdf}")
print(f"Average 2KB: {avg_2kb:.4f}%")
print(f"Average 4KB: {avg_4kb:.4f}%")
print(f"Average 8KB: {avg_8kb:.4f}%")
