#!/usr/bin/env python3
"""
Master Execution Script for FedGen-Rare:
Privacy-Preserving Federated Generative Replay for Rare Disease Diagnosis.

Usage:
    python run.py --mode benchmark    # Run 4-way comparative benchmark (FedAvg vs FedProx vs FedIIC vs FedGen-Rare)
    python run.py --mode train        # Train standalone FedGen-Rare model with checkpoints
    python run.py --mode quicktest    # Fast 3-round test run on lightweight dataset
    python run.py --mode results      # Display latest saved benchmark metrics
    python run.py                     # Interactive selection menu
"""
import os
import sys
import argparse
import subprocess
import pandas as pd

SDP_DIR = os.path.dirname(os.path.abspath(__file__))
FEDGEN_DIR = os.path.join(SDP_DIR, "fedgen_rare")

def run_benchmark(rounds=12, clients=5, samples=900, alpha=0.25, backbone='convnet'):
    print("\n" + "="*70)
    print("  LAUNCHING 4-WAY COMPARATIVE BENCHMARK")
    print(f"  Methods: FedAvg | FedProx | FedIIC (MICCAI '23) | FedGen-Rare (Ours)")
    print(f"  Rounds: {rounds} | Hospital Clients: {clients} | Samples: {samples} | Alpha: {alpha}")
    print("="*70 + "\n")
    
    cmd = [
        sys.executable, "run_benchmark.py",
        "--rounds", str(rounds),
        "--clients", str(clients),
        "--samples", str(samples),
        "--alpha", str(alpha),
        "--backbone", backbone
    ]
    subprocess.run(cmd, cwd=FEDGEN_DIR, check=True)

def run_train(rounds=15, clients=5, samples=1000, alpha=0.25, backbone='convnet'):
    print("\n" + "="*70)
    print("  TRAINING STANDALONE FEDGEN-RARE (FEDERATED GENERATIVE REPLAY)")
    print(f"  Target: Idiopathic Pulmonary Fibrosis (IPF)")
    print(f"  Rounds: {rounds} | Hospital Clients: {clients} | Backbone: {backbone}")
    print("="*70 + "\n")
    
    cmd = [
        sys.executable, "train_fedgen.py",
        "--rounds", str(rounds),
        "--clients", str(clients),
        "--samples", str(samples),
        "--alpha", str(alpha),
        "--backbone", backbone,
        "--save_dir", "checkpoints"
    ]
    subprocess.run(cmd, cwd=FEDGEN_DIR, check=True)

def run_quicktest():
    print("\n" + "="*70)
    print("  RUNNING QUICK SMOKE TEST (Fast 3-round run)")
    print("="*70 + "\n")
    run_benchmark(rounds=3, clients=3, samples=300)

def show_results():
    results_path = os.path.join(FEDGEN_DIR, "experiments", "results", "benchmark_results.csv")
    if os.path.exists(results_path):
        print("\n" + "="*80)
        print("                 LATEST BENCHMARK RESULTS (TEST SET)")
        print("="*80)
        df = pd.read_csv(results_path, index_col=0)
        print(df.to_string())
        print("="*80)
        print(f"\nPlots available at:")
        print(f"  - Comparison: {os.path.join(FEDGEN_DIR, 'experiments', 'results', 'benchmark_comparison.png')}")
        print(f"  - Client Skew: {os.path.join(FEDGEN_DIR, 'experiments', 'results', 'client_distribution.png')}")
        print(f"  - Confusion:  {os.path.join(FEDGEN_DIR, 'experiments', 'results', 'confusion_matrices.png')}\n")
    else:
        print("\n[Notice] No benchmark results found yet. Run 'python run.py --mode benchmark' first.")

def interactive_menu():
    while True:
        print("\n" + "="*60)
        print("     FEDGEN-RARE: EXECUTION & BENCHMARK MENU")
        print("="*60)
        print("  1. Run 4-Way Comparative Benchmark (FedAvg, FedProx, FedIIC, FedGen-Rare)")
        print("  2. Train Standalone FedGen-Rare (Save Generator & Classifier Checkpoints)")
        print("  3. Run Fast Quick-Test (3 Rounds, Light Dataset)")
        print("  4. View Latest Benchmark Results & Metrics")
        print("  5. Exit")
        print("="*60)
        
        choice = input("Enter choice [1-5]: ").strip()
        if choice == '1':
            rounds = input("Enter number of communication rounds (default 10): ").strip()
            rounds = int(rounds) if rounds else 10
            run_benchmark(rounds=rounds)
        elif choice == '2':
            rounds = input("Enter number of training rounds (default 12): ").strip()
            rounds = int(rounds) if rounds else 12
            run_train(rounds=rounds)
        elif choice == '3':
            run_quicktest()
        elif choice == '4':
            show_results()
        elif choice == '5':
            print("Exiting.")
            break
        else:
            print("Invalid choice, please select 1-5.")

def main():
    parser = argparse.ArgumentParser(description="FedGen-Rare Runner")
    parser.add_argument('--mode', type=str, choices=['benchmark', 'train', 'quicktest', 'results', 'interactive'],
                        default='interactive', help='Execution mode')
    parser.add_argument('--rounds', type=int, default=10, help='Communication rounds')
    parser.add_argument('--clients', type=int, default=5, help='Number of hospital clients')
    parser.add_argument('--samples', type=int, default=800, help='Total samples across consortium')
    parser.add_argument('--alpha', type=float, default=0.25, help='Dirichlet Non-IID parameter')
    parser.add_argument('--backbone', type=str, default='convnet', choices=['convnet', 'resnet18'])
    args = parser.parse_args()

    if args.mode == 'benchmark':
        run_benchmark(rounds=args.rounds, clients=args.clients, samples=args.samples, alpha=args.alpha, backbone=args.backbone)
    elif args.mode == 'train':
        run_train(rounds=args.rounds, clients=args.clients, samples=args.samples, alpha=args.alpha, backbone=args.backbone)
    elif args.mode == 'quicktest':
        run_quicktest()
    elif args.mode == 'results':
        show_results()
    else:
        interactive_menu()

if __name__ == '__main__':
    main()
