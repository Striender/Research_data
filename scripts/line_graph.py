import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# ── Raw Data Table ────────────────────────────────────────────────────────────
raw_table = """
bark.coarse_token_gen.1	97.8546	15.2822	9.94498	13.2076	6.15692	6.25267	6.05497
bark.coarse_token_gen.2	108.385	63.1519	59.7933	59.0277	12.9911	11.4386	7.78871
bark.coarse_token_gen.3	66.0007	18.2955	12.0892	9.21678	6.34256	3.99141	2.82896
bark.coarse_token_gen.4	108.145	72.7511	68.5927	66.6246	14.329	12.0386	7.69765
bark.coarse_token_gen.5	51.1999	50.8515	50.69	50.6388	50.5523	50.1182	26.18
bark.semantic_token_gen.1	105.467	57.7362	52.5382	52.9344	12.2023	10.7035	7.41758
bark.semantic_token_gen.2	96.7576	15.1482	9.78177	13.3586	6.50621	6.54829	6.3478
bark.semantic_token_gen.3	54.989	54.5887	54.3727	54.2972	53.8762	53.684	31.7494
bark.semantic_token_gen.4	53.8895	53.515	53.3205	53.2573	52.9314	52.6897	30.2031
bark.semantic_token_gen.5	51.8568	51.5014	51.3334	51.2743	51.1194	50.7042	28.2896
clip_trace_1	63.2752	60.7407	9.35122	10.1238	4.15248	3.9651	3.6585
clip_trace_2	29.9136	25.5796	7.68642	6.48535	2.73036	2.60724	2.60134
clip_trace_3	62.1888	59.7775	10.6435	10.7151	5.27445	5.08879	4.84807
clip_trace_4	34.2292	29.4853	18.7913	17.5326	9.71732	5.60272	4.38017
clip_trace_5	62.4806	54.9864	11.3776	10.3597	4.81252	4.66516	4.53088
llama2.c-llama2_7b.1	63.2311	35.6978	35.5557	35.5538	35.553	35.553	35.5529
llama2.c-llama2_7b.10	64.5749	42.4239	39.5796	35.608	35.5715	35.5715	35.5715
llama2.c-llama2_7b.11	66.7769	49.622	43.9105	35.6528	35.5976	35.5975	35.5975
llama2.c-llama2_7b.12	65.3595	44.4713	40.804	35.6267	35.5837	35.5837	35.5837
llama2.c-llama2_7b.13	65.4774	47.0722	42.4339	35.6744	35.6221	35.6221	35.6221
llama2.c-llama2_7b.14	62.9676	35.6627	35.558	35.5571	35.5537	35.5535	35.5535
llama2.c-llama2_7b.15	66.7458	49.6786	43.9136	35.6563	35.5988	35.5988	35.5988
llama2.c-llama2_7b.16	66.4192	48.4814	43.1881	35.6451	35.5925	35.5925	35.5925
llama2.c-llama2_7b.2	66.3906	49.6212	43.8582	35.6181	35.5573	35.5569	35.5568
llama2.c-llama2_7b.3	62.874	35.6896	35.5563	35.5552	35.5521	35.5518	35.5517
llama2.c-llama2_7b.4	65.4358	44.4787	40.8088	35.6265	35.5837	35.5837	35.5837
llama2.c-llama2_7b.6	62.8751	35.6897	35.5562	35.5548	35.5516	35.5509	35.5509
llama2.c-llama2_7b.7	65.6205	44.5539	40.8506	35.6279	35.5839	35.5839	35.5839
llama2.c-llama2_7b.8	66.6455	49.6599	43.9138	35.6566	35.5989	35.5988	35.5988
llama2.c-llama2_7b.9	63.2669	36.8872	36.2676	35.5815	35.5561	35.5554	35.5553
llama2.c-stories110M.1	33.85	33.8306	33.825	33.8226	33.7351	33.7193	33.697
llama2.c-stories110M.2	33.4043	33.3768	33.3721	33.3639	33.0752	33.0578	33.0354
llama2.c-stories110M.3	33.4118	33.3634	33.3505	33.3471	33.0526	33.0293	33.0076
llama2.c-stories15M.1	34.7235	34.7098	34.7079	34.7074	34.7055	34.7022	34.693
llama2.c-stories15M.2	34.6993	34.6856	34.6734	34.6688	34.6658	34.6615	34.6506
llama2.c-stories15M.3	34.7243	34.7132	34.7109	34.6976	34.691	34.6875	34.6789
llama2.c-stories42M.1	35.0607	35.0019	35.0014	35.0012	35.0004	34.9989	34.9957
llama2.c-stories42M.2	35.0684	35.0052	35.0045	35.0043	35.0034	35.002	34.9989
llama2.c-stories42M.3	35.0678	35.0055	35.0036	35.0032	35.0024	35.0009	34.9978
sd.cpp-sd-v1-4.ckpt.1	247.993	247.446	240.192	239.397	140.16	131.514	124.842
sd.cpp-sd-v1-4.ckpt.2	223.107	132.371	127.807	127.781	121.088	23.1605	19.9616
sd.cpp-sd-v1-4.ckpt.3	0.95041	0.933325	0.92615	0.92232	0.9214	0.9214	0.9214
sd.cpp-sd-v1-4.ckpt.4	93.3634	91.1958	89.0528	86.3528	17.3715	15.8101	8.20468
sd.cpp-sd-v1-4.ckpt.5	619.377	367.237	336.264	333.195	332.838	114.205	35.5334
sd.cpp-v1-5-pruned-emaonly.1	0.967145	0.933725	0.92645	0.922355	0.9214	0.9214	0.9214
sd.cpp-v1-5-pruned-emaonly.2	141.431	140.818	136.722	136.136	70.2349	64.0489	58.8227
sd.cpp-v1-5-pruned-emaonly.3	379.2	255.423	233.725	230.216	225.005	41.7363	20.1513
sd.cpp-v1-5-pruned-emaonly.4	223.327	131.825	127.771	127.771	121.079	23.3209	19.8933
sd.cpp-v1-5-pruned-emaonly.5	0.950105	0.933385	0.92651	0.922195	0.9212	0.9212	0.9212
sd.cpp-v2-1_768-nonema-pruned.1	172.683	170.165	169.659	169.568	28.9854	12.4374	12.153
sd.cpp-v2-1_768-nonema-pruned.2	245.901	237.686	139.18	136.491	130.26	123.465	25.1849
sd.cpp-v2-1_768-nonema-pruned.3	223.399	132.077	127.808	127.78	121.103	23.4594	19.967
sd.cpp-v2-1_768-nonema-pruned.4	620.319	362.438	332.42	329.787	329.489	329.489	37.9783
sd.cpp-v2-1_768-nonema-pruned.5	92.8969	90.8814	88.794	86.2057	19.621	18.063	10.3318
vit.cpp-base-ggml-model.1	67.3049	49.7613	48.1917	48.0978	9.39614	7.22869	4.77746
vit.cpp-base-ggml-model.2	45.7751	10.781	7.80156	7.48348	4.48787	3.71519	3.68524
vit.cpp-large-ggml-model.1	64.5447	49.3172	28.2415	25.3109	23.0883	5.59873	4.87915
vit.cpp-large-ggml-model.2	62.0886	42.0119	8.37359	5.49824	4.09861	3.76677	3.70333
vit.cpp-large-ggml-model.3	41.1908	26.4296	8.20974	4.68769	3.16436	2.98581	2.94929
vit.cpp-large-ggml-model.4	62.2702	41.8667	8.7544	5.36733	3.97978	3.66452	3.59146
whisper_trace_1	113.063	106.843	20.5518	18.3146	7.40443	7.14778	6.60074
whisper_trace_2	113.073	106.569	20.9593	18.132	7.37766	7.13122	6.59436
whisper_trace_3	113.063	106.88	20.7309	18.1729	7.42819	7.16395	6.60361
whisper_trace_4	98.256	83.1778	54.8485	44.4093	41.5339	19.0194	18.6117
whisper_trace_5	84.9536	76.8524	68.4756	63.6116	23.576	19.897	17.3117
whisper_trace_6	112.687	100.82	86.8236	78.6277	10.9775	5.07439	1.1338
whisper_trace_7	90.343	78.1718	51.9014	41.6222	37.5676	18.2436	17.6401
whisper_trace_8	113.055	106.574	22.4933	17.8516	7.49093	7.29171	7.39184
"""

cache_sizes = ["16 KB", "32 KB", "48 KB", "64 KB", "128 KB", "256 KB", "512 KB"]
workloads = []
data_rows = []

for line in raw_table.strip().split("\n"):
    if not line.strip():
        continue
    parts = line.strip().split("\t")
    workloads.append(parts[0].strip())
    data_rows.append([float(x.strip()) for x in parts[1:]])

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

# ── PLOT 1: All Workloads on X-axis, 7 Cache Sizes as Lines ─────────────────────
xp = [0.0, 100.0, 200.0, 400.0, 600.0, 650.0]
fp = [0.0, 0.48, 0.65, 0.82, 0.96, 1.00]

def forward(y):
    y = np.asarray(y, dtype=float)
    return np.interp(y, xp, fp)

def inverse(v):
    v = np.asarray(v, dtype=float)
    return np.interp(v, fp, xp)

# 7 shades from the blue-grey palette with distinct markers
colors_7 = ['#A8C0E0', '#85A0C8', '#6382AE', '#4A6894', '#364D73', '#253550', '#151F30']
markers_7 = ['o', 's', '^', 'D', 'v', 'p', 'X']
params = {
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

# Ticks exactly as requested by user: 0, 20, 40, 60, 80, 100, then 200, 400, 600
y_ticks = [0, 20, 40, 60, 80, 100, 200, 400, 600]
ax.set_yticks(y_ticks)
ax.set_ylim(0, 650)

ax.set_ylabel('L1D MPKI')
#ax.set_xlabel('AI_ML Workload')
ax.set_xticks(x_idx)
ax.set_xticklabels(plot_workloads, rotation=90, ha='center')
ax.set_xlim(-1.0, len(plot_workloads) + 0.5)

ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='black', framealpha=1.0, fancybox=False, ncol=2)

sample_dir = "../plots/cache_sensitivity/"
os.makedirs(sample_dir, exist_ok=True)

plt.savefig(os.path.join(sample_dir, 'l1d_mpki.png'), bbox_inches='tight')
#plt.savefig(os.path.join(sample_dir, 'distribution_of_bingo-l2_MSHR_Full_events.pdf'), bbox_inches='tight')
plt.close()

print("Successfully generated stacked bar sample plot with font size 15.")