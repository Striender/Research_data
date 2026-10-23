import os
import shutil
import numpy as np
import matplotlib.pyplot as plt

# ── 68 AI/ML Workload Traces ───────────────────────────────────────────────────
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
]

# ── Raw Data Table ────────────────────────────────────────────────────────────
raw_table = """
2.5975	2.2325	2.0341	2.0539	1.3246	1.2311	1.2697
3.3267	2.9146	2.6325	2.6797	2.3122	2.3492	2.3758
1.3654	1.2593	1.1091	1.0958	1.0792	1.0916	1.143
3.8446	3.672	3.3917	3.4035	3.1455	3.0177	2.8788
14.7915	14.0695	13.8676	13.724	13.5642	13.6901	13.4778
3.645	3.2456	3.0441	2.9966	2.6251	2.4534	2.3898
2.272	2.1154	2.1017	1.9429	1.4719	1.468	1.687
18.34	17.9666	17.7195	17.6061	17.4837	17.2785	17.0528
17.6239	17.1519	16.8219	16.7668	16.5869	16.2215	15.7836
15.7923	15.249	14.9732	14.8245	14.6415	14.5164	14.2659
0.4073	0.4366	0.3494	0.2861	0.2777	0.2545	0.2552
0.3271	0.3065	0.2975	0.2782	0.2743	0.2827	0.2747
0.8604	0.8552	0.8243	0.8288	0.7951	0.7654	0.7805
1.0278	1.0581	0.9405	0.949	0.9005	0.9182	0.9829
0.4566	0.4363	0.4517	0.4173	0.4059	0.417	0.425
1.5836	0.9912	0.9297	0.9282	0.9376	0.9342	0.9566
1.8834	1.2971	1.2454	1.2465	1.1871	1.1983	1.2279
1.7101	1.0979	1.0389	1.0394	1.0435	1.0483	1.0708
1.5875	1.0316	0.9771	0.978	0.9389	0.943	0.9505
1.7783	1.0803	1.0569	1.0608	1.0622	1.0699	1.1015
1.6244	1.0489	1.0271	1.0189	0.9881	0.9893	0.9946
1.7929	1.2396	1.1951	1.2004	1.1423	1.1445	1.1632
1.6812	1.0791	1.0122	1.0118	1.0114	1.0247	1.0428
1.7818	1.1877	1.1135	1.1157	1.0907	1.0973	1.1076
1.6908	1.2077	1.166	1.1733	1.1128	1.1195	1.1209
1.635	1.0891	1.0341	1.0298	0.9962	0.9955	0.9948
1.7836	1.3314	1.2836	1.2818	1.2311	1.234	1.2345
1.7534	1.1377	1.1084	1.1114	1.1162	1.1299	1.146
1.7885	1.2415	1.1926	1.2001	1.1356	1.1427	1.1543
1.6717	1.1065	1.0545	1.0465	0.9957	0.9988	1.0036
1.0615	1.0563	1.0547	1.0576	1.0851	1.0933	1.1868
1.0852	1.0587	1.0611	1.062	1.0811	1.1038	1.1881
1.0389	1.0355	1.0283	1.0317	1.0413	1.0585	1.1482
1.2826	1.2811	1.2915	1.3015	1.3423	1.4336	1.7179
1.2843	1.2897	1.2934	1.3087	1.3334	1.4327	1.6674
1.2686	1.274	1.2845	1.3028	1.3522	1.5078	1.9932
0.9025	0.8882	0.8883	0.8924	0.9106	0.9417	1.114
0.9467	0.9252	0.9249	0.927	0.9472	0.9986	1.2205
0.904	0.8874	0.8858	0.8886	0.8949	0.8905	0.9057
10.9779	10.6624	10.7772	10.256	7.8019	8.1881	8.6374
6.9913	6.2621	6.1919	6.0159	5.9877	6.0221	5.9914
0.0061	0.0049	0.0038	0.0041	0.0036	0.0045	0.0052
4.7217	4.3877	4.2169	4.3134	4.3045	4.2887	4.2906
2.1949	1.0238	0.8296	0.8712	0.6882	0.728	0.5692
0.0022	0.0014	0.001	0.0011	0.0014	0.0011	0.0013
3.3116	2.9783	2.9749	2.9966	3.1541	3.9103	4.3312
15.2634	15.0842	15.0261	14.8888	14.8497	14.7321	14.7816
6.9689	6.3965	6.1944	6.0646	5.9881	5.9177	5.8324
0.0024	0.0011	0.0012	0.0012	0.0013	0.0014	0.0015
9.9229	9.8938	9.8935	9.8926	9.8429	9.822	9.8359
7.9043	7.5629	7.0014	6.7964	6.792	6.6761	6.2418
6.9912	6.3377	6.2163	6.092	6.0488	5.9602	5.8918
1.4972	0.722	0.5969	0.5962	0.5103	0.5231	0.4664
4.1666	3.9299	3.8406	3.8187	3.7355	3.8025	3.7038
0.4788	0.4762	0.4297	0.4138	0.378	0.3694	0.3796
0.468	0.3927	0.37	0.3739	0.3475	0.355	0.368
0.4879	0.4272	0.2945	0.281	0.2855	0.2858	0.3031
0.444	0.4463	0.2693	0.337	0.3151	0.2043	0.1843
0.446	0.3458	0.2711	0.267	0.2687	0.2869	0.3123
0.3173	0.3555	0.2504	0.2943	0.2769	0.2278	0.2167
4.4763	4.3357	4.341	4.0131	3.7303	3.4709	3.4733
4.3565	4.275	4.373	4.1261	3.7267	3.543	3.5166
4.228	4.1136	4.2327	4.0153	3.6369	3.38	3.383
11.9758	11.3739	11.4514	10.7315	10.7225	10.4123	10.3324
16.2568	15.5396	15.4777	15.3826	15.181	15.1097	15.1083
0.6594	0.6044	0.5785	0.5843	0.3797	0.3231	0.3091
11.3808	10.7949	10.9454	10.1037	10.0153	9.6855	9.5783
3.061	2.9296	2.6068	2.2356	1.0771	1.3812	1.1408
"""

cache_sizes = ["16 KB", "32 KB", "48 KB", "64 KB", "128 KB", "256 KB", "512 KB"]
data_rows = []
for line in raw_table.strip().split("\n"):
    if not line.strip():
        continue
    data_rows.append([float(x.strip()) for x in line.strip().split("\t")])

data_arr = np.array(data_rows)  # shape (68, 7)
avg_row = np.mean(data_arr, axis=0)  # shape (7,)

plot_workloads = workloads + ["Average"]
plot_data = np.vstack([data_arr, avg_row])  # shape (69, 7)

# ── Styling Parameters (Thesis.ipynb / AGENTS.md) ──────────────────────────────
scale = 1.5
fig_width_pt = 240.94499
inches_per_pt = 1.0 / 72.27
golden_mean = 0.6
fig_width = fig_width_pt * inches_per_pt * scale  # ~5.0 inches
fig_height = fig_width * golden_mean * 0.95      # ~2.85 inches

# Piecewise scaling for Y axis:
# 0 to 100 occupies 55% of vertical space
# 100 to 420 occupies 45% of vertical space
xp = [0.0, 100.0, 200.0, 300.0, 400.0, 420.0]
fp = [0.0, 0.52, 0.70, 0.85, 0.98, 1.00]

def forward(y):
    y = np.asarray(y, dtype=float)
    return np.interp(y, xp, fp)

def inverse(v):
    v = np.asarray(v, dtype=float)
    return np.interp(v, fp, xp)

# 7 shades from the blue-grey palette with distinct markers
colors_7 = ['#A8C0E0', '#85A0C8', '#6382AE', '#4A6894', '#364D73', '#253550', '#151F30']
markers_7 = ['o', 's', '^', 'D', 'v', 'p', 'X']

# ── PLOT 1: All Workloads on X-axis, 7 Cache Sizes as Lines ─────────────────────
params_p1 = {
    'figure.dpi': 300,
    'backend': 'ps',
    'axes.labelsize': 5.0 * scale,
    'font.size': 3.0 * scale,
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
plt.rcParams.update(params_p1)

fig, ax = plt.subplots()
ax.set_yscale('function', functions=(forward, inverse))

x_idx = np.arange(len(plot_workloads))

for i, (size_label, color, marker) in enumerate(zip(cache_sizes, colors_7, markers_7)):
    y_vals = plot_data[:, i]
    # Workloads 0..67
    ax.plot(x_idx[:-1], y_vals[:-1], label=size_label, color=color, marker=marker,
            markersize=2.2, markeredgecolor='black', markeredgewidth=0.3, linewidth=0.8)
    # Average point at index 68
    ax.plot(x_idx[-1:], y_vals[-1:], color=color, marker=marker,
            markersize=4.8, markeredgecolor='black', markeredgewidth=0.6)
    # Dotted connection to Average
    ax.plot(x_idx[-2:], y_vals[-2:], color=color, linestyle=':', linewidth=0.75)

# Vertical divider before Average
ax.axvline(x=len(plot_workloads) - 1.5, color='black', linestyle='-', linewidth=0.6, alpha=0.5)

# Ticks: 0, 20, 40, 60, 80, 100, then 200, 300, 400
y_ticks = [0,4,8,12,16, 20]#, 20, 30, 40]
ax.set_yticks(y_ticks)
ax.set_ylim(0, 20)

ax.set_ylabel('L2 MPKI')
ax.set_xticks(x_idx)
ax.set_xticklabels(plot_workloads, rotation=90, ha='center')
ax.set_xlim(-1.0, len(plot_workloads) + 0.5)

ax.legend(loc='upper right', bbox_to_anchor=(0.9, 1.01),frameon=True, facecolor='white', edgecolor='black', framealpha=1.0, fancybox=False, ncol=2)

sample_dir = "../plots/cache_sensitivity/"
os.makedirs(sample_dir, exist_ok=True)

plt.savefig(os.path.join(sample_dir, 'L2_MPKI_with_PF_bingo.png'), bbox_inches='tight')
#plt.savefig(os.path.join(sample_dir, 'distribution_of_bingo-l2_MSHR_Full_events.pdf'), bbox_inches='tight')
plt.close()

print("Successfully generated stacked bar sample plot with font size 15.")

