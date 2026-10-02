#!/usr/bin/env python3
"""
Comprehensive 4-Way Federated Learning Benchmark for Rare Disease Diagnosis:
Compares FedAvg, FedProx, FedIIC (MICCAI '23), and FedGen-Rare (Ours) on Idiopathic Pulmonary Fibrosis (IPF).
"""
import os
import sys
import argparse
import copy
import pandas as pd
import numpy as np
import torch

# Ensure fedgen_rare root is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import Config
from datasets.ipf_dataset import get_ipf_federated_environment
from federated.client import HospitalClient
from federated.server import FederatedServer
from utils.visualization import (
    plot_benchmark_comparison,
    plot_client_distribution,
    plot_confusion_matrices
)

def parse_args():
    parser = argparse.ArgumentParser(description="FedGen-Rare Multi-Method Benchmark")
    parser.add_argument("--rounds", type=int, default=10, help="Number of communication rounds")
    parser.add_argument("--clients", type=int, default=5, help="Number of hospital clients")
    parser.add_argument("--samples", type=int, default=800, help="Total dataset samples")
    parser.add_argument("--alpha", type=float, default=0.2, help="Dirichlet Non-IID skew parameter")
    parser.add_argument("--backbone", type=str, default="convnet", choices=["convnet", "resnet"], help="Backbone model")
    parser.add_argument("--output_dir", type=str, default="experiments/results", help="Directory to save artifacts")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    return parser.parse_args()

def run_benchmark():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Set seed
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    config = Config(
        num_clients=args.clients,
        non_iid_alpha=args.alpha,
        global_rounds=args.rounds,
        classifier_backbone=args.backbone,
        output_dir=args.output_dir,
        seed=args.seed
    )

    print("\n" + "="*80)
    print(" FEDERATED LEARNING BENCHMARK: RARE DISEASE DIAGNOSIS (IPF)")
    print(f" Target Disease:       Idiopathic Pulmonary Fibrosis (ORPHA:2032)")
    print(f" Total Cohort Size:    {args.samples} Chest HRCT Slices")
    print(f" Hospital Silos:       {args.clients} Independent Centers")
    print(f" Non-IID Dirichlet α:  {args.alpha} (Extreme Rarity & Skew)")
    print(f" Communication Rounds: {args.rounds}")
    print(f" Classifier Backbone:  {args.backbone}")
    print(f" Computing Device:     {config.device}")
    print("="*80 + "\n")

    # Step 1: Generate Multi-Center Non-IID Dataset with scanner domain shifts
    print("[1/4] Generating Multi-Center Non-IID HRCT Cohort...")
    client_datasets, test_dataset = get_ipf_federated_environment(
        num_clients=args.clients,
        alpha=args.alpha,
        num_samples=args.samples,
        test_ratio=0.25,
        seed=args.seed
    )

    # Instantiate Hospital Clients
    clients = [HospitalClient(i, client_datasets[i], config) for i in range(args.clients)]
    
    print("\n--- Hospital Silo Distribution ---")
    for c in clients:
        print(f"  Hospital {c.client_id+1}: Total={c.total_samples:3d} scans | IPF={c.rare_samples:2d} ({c.rare_samples/c.total_samples*100:4.1f}%) | COPD={c.class_counts[1]:2d} | Normal={c.class_counts[2]:2d}")
    print(f"  Held-out Global Test Set: {len(test_dataset)} scans (IPF={test_dataset.get_class_counts()[0]})\n")

    # Plot hospital distribution
    dist_plot_path = os.path.join(args.output_dir, "client_distribution.png")
    plot_client_distribution(clients, config.class_names, dist_plot_path)

    # Step 2: Benchmark Methods
    methods = [
        ("FedAvg", "train_round_fedavg"),
        ("FedProx", "train_round_fedprox"),
        ("FedIIC (MICCAI '23)", "train_round_fediic"),
        ("FedGen-Rare (Ours)", "train_round_fedgen_rare")
    ]

    benchmark_results = {}

    for method_name, train_method_attr in methods:
        print("\n" + "-"*70)
        print(f"  TRAINING METHOD: {method_name}")
        print("-"*70)

        # Fresh server with identical initial state
        torch.manual_seed(args.seed)
        server = FederatedServer(clients, test_dataset, config)
        train_round_fn = getattr(server, train_method_attr)

        for round_idx in range(1, args.rounds + 1):
            loss = train_round_fn()
            
            if round_idx % max(1, (args.rounds // 4)) == 0 or round_idx == args.rounds:
                eval_metrics = server.evaluate_global()
                print(f"  Round {round_idx:2d}/{args.rounds:2d} | Loss: {loss:.4f} | "
                      f"Acc: {eval_metrics['accuracy']*100:5.1f}% | "
                      f"Balanced Acc: {eval_metrics['balanced_accuracy']*100:5.1f}% | "
                      f"IPF Recall: {eval_metrics['rare_recall']*100:5.1f}% | "
                      f"IPF F1: {eval_metrics['rare_f1']*100:5.1f}%")

        final_metrics = server.evaluate_global()
        benchmark_results[method_name] = final_metrics

    # Step 3: Compile and Save Benchmark Results
    print("\n" + "="*85)
    print("                    FINAL BENCHMARK COMPARISON TABLE")
    print("="*85)

    summary_rows = []
    for method_name, metrics in benchmark_results.items():
        summary_rows.append({
            'Method': method_name,
            'Balanced Acc (%)': round(metrics['balanced_accuracy'] * 100, 2),
            'IPF Recall (%)': round(metrics['rare_recall'] * 100, 2),
            'IPF Precision (%)': round(metrics['rare_precision'] * 100, 2),
            'IPF F1-Score (%)': round(metrics['rare_f1'] * 100, 2),
            'Macro F1 (%)': round(metrics['macro_f1'] * 100, 2),
            'Overall Acc (%)': round(metrics['accuracy'] * 100, 2),
            'ROC-AUC': round(metrics['auc_roc'], 4)
        })

    df = pd.DataFrame(summary_rows).set_index('Method')
    print(df.to_string())
    print("="*85)

    csv_path = os.path.join(args.output_dir, "benchmark_results.csv")
    df.to_csv(csv_path)
    print(f"\n[Saved Results CSV] {csv_path}")

    # Step 4: Generate Publication-Grade Visualizations
    comp_plot_path = os.path.join(args.output_dir, "benchmark_comparison.png")
    plot_benchmark_comparison(benchmark_results, comp_plot_path)

    cm_plot_path = os.path.join(args.output_dir, "confusion_matrices.png")
    plot_confusion_matrices(benchmark_results, ['IPF', 'COPD', 'Normal'], cm_plot_path)

    print("\n[Done] Benchmark execution completed successfully.")

if __name__ == "__main__":
    run_benchmark()

