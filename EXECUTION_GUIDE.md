# FedGen-Rare: Execution & GitHub Push Guide

This guide provides instructions on how to run the codebase, reproduce benchmarks, and push the repository to GitHub.

---

## 1. Environment Setup

Make sure your Python environment has the required dependencies installed:

```bash
pip install -r requirements.txt
```

Verified dependencies:
* `torch >= 2.0.0`
* `torchvision >= 0.15.0`
* `scikit-learn >= 1.2.0`
* `pandas >= 1.5.0`
* `numpy >= 1.22.0`
* `matplotlib >= 3.5.0`
* `pillow >= 9.0.0`

---

## 2. How to Execute the Code

We provide a master runner script (`run.py` and `run.sh`) located in the root folder.

### Option A: Interactive Menu (Recommended)
Simply execute:
```bash
python3 run.py
```
Or on Linux / macOS / WSL:
```bash
./run.sh
```
This presents an interactive menu to choose between benchmarking, training, quick smoke testing, or viewing saved results.

---

### Option B: Command-Line Flags

#### 1. Run the 4-Way Comparative Benchmark
Evaluates **FedAvg**, **FedProx**, **FedIIC (MICCAI '23)**, and **FedGen-Rare (Ours)** on the multi-center non-IID Idiopathic Pulmonary Fibrosis (IPF) dataset:
```bash
python3 run.py --mode benchmark --rounds 12 --clients 5 --samples 900
```
**Outputs Generated in `fedgen_rare/experiments/results/`:**
* `benchmark_results.csv`: Table containing Accuracy, Balanced Accuracy (BACC), Macro-F1, Rare-Class Recall, and AUROC for all 4 methods.
* `benchmark_comparison.png`: High-resolution convergence curves across communication rounds.
* `client_distribution.png`: Non-IID distribution chart illustrating severe rare-disease scarcity across hospital silos.
* `confusion_matrices.png`: Side-by-side clinical diagnostic confusion matrices.

#### 2. Standalone Training of FedGen-Rare
Trains the Two-Stage Federated Latent Feature Generative Replay model and saves best generator and classifier checkpoints:
```bash
python3 run.py --mode train --rounds 15 --clients 5 --backbone convnet
```
Model checkpoints will be saved to:
* `fedgen_rare/checkpoints/best_classifier.pth`
* `fedgen_rare/checkpoints/best_generator.pth`

#### 3. Quick Smoke Test (Fast Verification)
Runs a fast 3-round benchmark on a smaller cohort to verify functionality within seconds:
```bash
python3 run.py --mode quicktest
```

#### 4. View Latest Results
Prints the latest benchmark evaluation table directly in the terminal:
```bash
python3 run.py --mode results
```

---

## 3. How to Push this Code to GitHub

Follow these steps to initialize and push this project to your GitHub account:

### Step 1: Create a New Repository on GitHub
1. Go to [GitHub](https://github.com/new).
2. Set Repository Name (e.g., `fedgen-rare` or `sdp-federated-rare-disease`).
3. Set visibility to **Public** or **Private**.
4. **Do NOT** check "Initialize with README", ".gitignore", or "license" (we already configured these locally).
5. Click **Create repository**.
6. Copy the repository URL (e.g., `https://github.com/<your-username>/fedgen-rare.git`).

---

### Step 2: Initialize Git and Commit Locally

Open your terminal in this project folder (`/run/media/aditya/Windows/sdp/`):

```bash
# 1. Initialize git
git init

# 2. Stage all files (the provided .gitignore prevents committing temporary files and large checkpoints)
git add .

# 3. Check status to verify staged files
git status

# 4. Commit your files
git commit -m "feat: Initial commit for FedGen-Rare framework with multi-center benchmark"
```

---

### Step 3: Link to GitHub and Push

```bash
# 1. Rename local branch to main
git branch -M main

# 2. Add your remote GitHub repository (replace with your actual GitHub URL)
git remote add origin https://github.com/<your-username>/<repo-name>.git

# 3. Push code to GitHub
git push -u origin main
```

> **Note on Authentication:**
> When prompted for your password:
> * GitHub no longer accepts account passwords for git operations.
> * Use a **Personal Access Token (Classic)** with `repo` scope.
> * Generate one at: [GitHub Settings -> Developer Settings -> Personal access tokens](https://github.com/settings/tokens).
> * Alternatively, if you use SSH: `git remote add origin git@github.com:<your-username>/<repo-name>.git`

---

## 4. Repository Layout

```
.
├── .gitignore                   # Excludes __pycache__, checkpoints, logs, and temp files
├── requirements.txt             # PyTorch, Scikit-Learn, Pandas, Matplotlib dependencies
├── run.py                       # Master execution script (benchmark, train, quicktest, results)
├── run.sh                       # Bash script launcher
├── EXECUTION_GUIDE.md           # This execution and GitHub push guide
├── SDP Review_final.pptx        # Untouched original review presentation
├── fedgen_rare/                 # Primary FedGen-Rare framework
│   ├── config.py                # Hyperparameters & target rare disease config
│   ├── models/                  # Classifier backbones & Conditional Latent Feature Generator
│   ├── datasets/                # Multi-center Non-IID IPF HRCT partitioner
│   ├── federated/               # Hospital Client, Federated Server, and SOTA baselines
│   ├── utils/                   # Metrics (Macro-F1, BACC, Sensitivity) & Visualization plots
│   ├── run_benchmark.py         # 4-way comparative benchmark script
│   ├── train_fedgen.py          # Standalone training script with model checkpointing
│   ├── README.md                # Full clinical background and architecture documentation
│   └── experiments/results/     # Generated plots (PNG) and tabular metrics (CSV)
├── FedIIC_baseline/             # Official MICCAI '23 baseline implementation
└── DLPM_IPF_repo/               # Deep learning IPF prognostication baseline
```
