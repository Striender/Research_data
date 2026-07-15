# AI/ML ChampSim Experiment Runner

This script runs ChampSim experiments for AI/ML traces using different prefetcher and replacement-policy combinations.

## Script name

```bash
run_all_combination_ai_ml.sh
```

## Basic syntax

```bash
./run_all_combination_ai_ml.sh <TOTAL_CORES> [RP_SELECTOR] [MODE]
```

### Arguments

| Argument      | Required | Description                                          |
| ------------- | -------: | ---------------------------------------------------- |
| `TOTAL_CORES` |      Yes | Maximum number of cores/process slots to use         |
| `RP_SELECTOR` |       No | Select one or more replacement-policy configurations |
| `MODE`        |       No | Use `p` to parallelize replacement policies          |

---

# Replacement-policy mapping

| RP number | L2 replacement | LLC replacement |
| --------: | -------------- | --------------- |
|         1 | LRU            | LRU             |
|         2 | LRU            | SRRIP           |
|         3 | LRU            | DRRIP           |
|         4 | LRU            | Hawkeye         |
|         5 | LRU            | SHIP            |
|         6 | LRU            | SHIP++          |
|         7 | LRU            | Mockingjay      |
|         8 | SRRIP          | LRU             |
|         9 | SRRIP          | SRRIP           |
|        10 | SRRIP          | DRRIP           |
|        11 | SRRIP          | Hawkeye         |
|        12 | SRRIP          | SHIP            |
|        13 | SRRIP          | SHIP++          |
|        14 | SRRIP          | Mockingjay      |

---

# Running all replacement policies sequentially

```bash
./run_all_combination_ai_ml.sh 120
```

This runs:

```text
RP1 → RP2 → RP3 → ... → RP14
```

In normal mode, multiple enabled prefetcher combinations may run in parallel depending on the available core budget.

---

# Running one replacement policy

Run only RP14:

```bash
./run_all_combination_ai_ml.sh 120 14
```

Expected output:

```text
RP_SELECTOR = 14
RP_LIST     = 14
```

Run only RP1:

```bash
./run_all_combination_ai_ml.sh 120 1
```

Run only RP7:

```bash
./run_all_combination_ai_ml.sh 120 7
```

---

# Running selected replacement policies sequentially

Run RP5, RP6, and RP14:

```bash
./run_all_combination_ai_ml.sh 120 rp:5,6,14
```

Expected output:

```text
RP_SELECTOR = rp:5,6,14
RP_LIST     = 5 6 14
```

Run only the LRU-based configurations:

```bash
./run_all_combination_ai_ml.sh 120 rp:1,2,3,4,5,6,7
```

Run only the SRRIP-based configurations:

```bash
./run_all_combination_ai_ml.sh 120 rp:8,9,10,11,12,13,14
```

---

# Parallel replacement-policy mode

Use `p` to run replacement policies in parallel.

```bash
./run_all_combination_ai_ml.sh 120 p
```

In this mode:

1. Prefetcher combinations run one after another.
2. Replacement policies within the current prefetcher combination run in parallel.
3. The number of simultaneously running replacement policies is controlled by:

```bash
MAX_PARALLEL_COMBOS=$(( TOTAL_CORES / CORES_PER_COMBO ))
```

For example:

```text
TOTAL_CORES = 120
CORES_PER_COMBO = 26

MAX_PARALLEL_COMBOS = 120 / 26 = 4
```

The execution pattern becomes:

```text
Prefetcher combination 1:
    RP1 + RP2 + RP3 + RP4
    RP5 + RP6 + RP7 + RP8
    RP9 + RP10 + RP11 + RP12
    RP13 + RP14

Prefetcher combination 2:
    RP1 + RP2 + RP3 + RP4
    ...
```

The second prefetcher combination starts only after the first one has fully completed.

---

# Running selected replacement policies in parallel

Run RP5, RP6, and RP14 in parallel:

```bash
./run_all_combination_ai_ml.sh 120 rp:5,6,14 p
```

Run RP13 and RP14 in parallel:

```bash
./run_all_combination_ai_ml.sh 120 rp:13,14 p
```

Run all LRU-based policies in parallel:

```bash
./run_all_combination_ai_ml.sh 120 rp:1,2,3,4,5,6,7 p
```

Run all SRRIP-based policies in parallel:

```bash
./run_all_combination_ai_ml.sh 120 rp:8,9,10,11,12,13,14 p
```

---

# Running one replacement policy with `p`

This is valid, although parallel mode is unnecessary when only one RP is selected:

```bash
./run_all_combination_ai_ml.sh 120 14 p
```

It runs only RP14.

---

# Current active prefetcher combination

The current script contains:

```bash
PREFETCHER_COMBINATIONS=(
  "no:sms"
)
```

Therefore, the active configuration is:

```text
L1D prefetcher: no
L2 prefetcher: SMS
```

The output directory is:

```text
./results/ai_ml/SMS/pref_l2/sms/
```

For RP14, the output directory will be:

```text
./results/ai_ml/SMS/pref_l2/sms/exp14_srrip_mockingjay/
```

---

# Enable more prefetcher combinations

Uncomment or add entries inside:

```bash
PREFETCHER_COMBINATIONS=(
  "vberti:bingo_dpc3"
  "vberti:ip_stride"
  "no:sms"
  "no:no"
)
```

Format:

```text
L1_PREFETCHER:L2_PREFETCHER
```

Examples:

```bash
"vberti:bingo_dpc3"
"ipcp_isca2020:spp"
"mlop_dpc3:ip_stride"
"no:sms"
"no:no"
```

---

# Trace filtering

The following traces are skipped:

```bash
SKIP_TRACE_PREFIXES=(
    rwkv
    biogpt.cpp-ggml-model-tocilizumab
)
```

Any trace whose filename begins with one of these prefixes will not run.

---

# Check the selected replacement policies

The script prints:

```text
RP_SELECTOR = ...
RP_LIST     = ...
```

For example:

```bash
./run_all_combination_ai_ml.sh 120 14
```

should print:

```text
RP_SELECTOR = 14
RP_LIST     = 14
```

If it prints:

```text
RP_SELECTOR =
RP_LIST     = 1 2 3 4 5 6 7 8 9 10 11 12 13 14
```

then the second argument was not passed to the script.

---

# Check running ChampSim processes

Count ChampSim-related processes:

```bash
pgrep -af champsim | wc -l
```

Show ChampSim processes:

```bash
pgrep -af champsim
```

Estimate the number of CPU cores currently used by ChampSim:

```bash
ps -eo %cpu,cmd | grep champsim | grep -v grep | \
awk '{sum+=$1} END {printf "Approx ChampSim cores in use: %.1f\n", sum/100}'
```

Check all CPU usage by the current user:

```bash
ps -u "$USER" -o %cpu= | \
awk '{sum+=$1} END {printf "Approx total cores in use: %.1f\n", sum/100}'
```

Monitor interactively:

```bash
htop
```

---

# Make the script executable

Run once:

```bash
chmod +x run_all_combination_ai_ml.sh
```

Then execute it using:

```bash
./run_all_combination_ai_ml.sh 120
```

---

# Common commands

```bash
# Run all RPs sequentially
./run_all_combination_ai_ml.sh 120

# Run only RP14
./run_all_combination_ai_ml.sh 120 14

# Run RP5, RP6, and RP14 sequentially
./run_all_combination_ai_ml.sh 120 rp:5,6,14

# Run all RPs in parallel mode
./run_all_combination_ai_ml.sh 120 p

# Run RP5, RP6, and RP14 in parallel mode
./run_all_combination_ai_ml.sh 120 rp:5,6,14 p

# Run only RP14 with p mode
./run_all_combination_ai_ml.sh 120 14 p
```

