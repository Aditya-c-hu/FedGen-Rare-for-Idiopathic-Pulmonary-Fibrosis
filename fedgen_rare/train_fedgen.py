#!/usr/bin/env python3
"""
Standalone Training Script for FedGen-Rare:
Privacy-Preserving Federated Generative Replay for Rare Pulmonary Fibrosis Diagnosis.
Saves checkpoints for both the Global Conditional Generator and the Global Diagnostic Classifier.
"""
import os
import sys
import argparse
import torch
import numpy as np

# Ensure fedgen_rare root is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import Config
from datasets.ipf_dataset import get_ipf_federated_environment
from federated.client import HospitalClient
from federated.server import FederatedServer

def parse_args():
    parser = argparse.ArgumentParser(description="Train Standalone FedGen-Rare")
    parser.add_argument("--rounds", type=int, default=12, help="Global communication rounds")
    parser.add_argument("--clients", type=int, default=5, help="Number of hospital clients")
    parser.add_argument("--samples", type=int, default=1000, help="Total dataset samples")
    parser.add_argument("--alpha", type=float, default=0.2, help="Dirichlet Non-IID skew parameter")
    parser.add_argument("--backbone", type=str, default="convnet", choices=["convnet", "resnet"], help="Backbone model")
    parser.add_argument("--save_dir", type=str, default="checkpoints", help="Directory to save model checkpoints")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.save_dir, exist_ok=True)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    config = Config(
        num_clients=args.clients,
        non_iid_alpha=args.alpha,
        global_rounds=args.rounds,
        classifier_backbone=args.backbone,
        seed=args.seed
    )

    print("\n" + "="*75)
    print(" FEDGEN-RARE STANDALONE MODEL TRAINING")
    print(f" Target Pathology:      Idiopathic Pulmonary Fibrosis (Rare)")
    print(f" Hospital Silos:        {args.clients}")
    print(f" Communication Rounds:  {args.rounds}")
    print(f" Checkpoints Directory: {args.save_dir}")
    print("="*75 + "\n")

    client_datasets, test_dataset = get_ipf_federated_environment(
        num_clients=args.clients,
        alpha=args.alpha,
        num_samples=args.samples,
        test_ratio=0.25,
        seed=args.seed
    )

    clients = [HospitalClient(i, client_datasets[i], config) for i in range(args.clients)]
    server = FederatedServer(clients, test_dataset, config)

    best_bacc = 0.0
    best_clf_path = os.path.join(args.save_dir, "classifier_ipf_best.pt")
    best_gen_path = os.path.join(args.save_dir, "generator_ipf_best.pt")

    for round_idx in range(1, args.rounds + 1):
        loss = server.train_round_fedgen_rare()
        metrics = server.evaluate_global()

        print(f"Round {round_idx:2d}/{args.rounds:2d} | Train Loss: {loss:.4f} | "
              f"Acc: {metrics['accuracy']*100:5.1f}% | "
              f"Balanced Acc: {metrics['balanced_accuracy']*100:5.1f}% | "
              f"IPF Recall: {metrics['rare_recall']*100:5.1f}% | "
              f"IPF F1: {metrics['rare_f1']*100:5.1f}%")

        if metrics['balanced_accuracy'] > best_bacc:
            best_bacc = metrics['balanced_accuracy']
            torch.save(server.global_classifier.state_dict(), best_clf_path)
            torch.save(server.global_generator.state_dict(), best_gen_path)

    # Save final models
    final_clf_path = os.path.join(args.save_dir, "classifier_ipf_final.pt")
    final_gen_path = os.path.join(args.save_dir, "generator_ipf_final.pt")
    torch.save(server.global_classifier.state_dict(), final_clf_path)
    torch.save(server.global_generator.state_dict(), final_gen_path)

    print("\n" + "="*75)
    print(" TRAINING COMPLETE")
    print(f" Best Balanced Accuracy: {best_bacc*100:.2f}%")
    print(f" Checkpoint Saved (Best Clf):  {best_clf_path}")
    print(f" Checkpoint Saved (Best Gen):  {best_gen_path}")
    print(f" Checkpoint Saved (Final Clf): {final_clf_path}")
    print(f" Checkpoint Saved (Final Gen): {final_gen_path}")
    print("="*75 + "\n")

if __name__ == "__main__":
    main()

