"""
Visualization utilities for Federated Learning benchmarks on rare disease diagnosis.
Generates comparative bar charts, Dirichlet client distributions, and confusion matrices.
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless mode for server / terminal execution
import matplotlib.pyplot as plt

def plot_benchmark_comparison(results_dict, output_path="experiments/results/benchmark_comparison.png"):
    """
    Plots a multi-metric comparative bar chart across federated methods.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    methods = list(results_dict.keys())
    metrics_to_plot = ['balanced_accuracy', 'rare_recall', 'rare_f1', 'macro_f1', 'accuracy']
    metric_labels = ['Balanced Acc', 'IPF Recall (Sens.)', 'IPF F1-Score', 'Macro F1', 'Accuracy']
    
    n_methods = len(methods)
    n_metrics = len(metrics_to_plot)
    
    x = np.arange(n_metrics)
    width = 0.8 / n_methods
    
    fig, ax = plt.subplots(figsize=(11, 6))
    
    colors = ['#7f8c8d', '#3498db', '#e67e22', '#2ecc71']
    
    for i, method in enumerate(methods):
        values = [results_dict[method].get(m, 0.0) * 100 for m in metrics_to_plot]
        offset = (i - (n_methods - 1) / 2) * width
        bars = ax.bar(x + offset, values, width, label=method, color=colors[i % len(colors)], edgecolor='black', alpha=0.9)
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold')
            
    ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
    ax.set_title('Diagnostic Performance on Idiopathic Pulmonary Fibrosis (Rare Target)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.legend(loc='upper right', framealpha=0.95, fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[Plot Saved] {output_path}")


def plot_client_distribution(clients, class_names=None, output_path="experiments/results/client_distribution.png"):
    """
    Plots stacked horizontal bar chart showing non-IID class distribution across hospital silos.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if class_names is None:
        class_names = ['IPF (Rare)', 'Common ILD / COPD', 'Normal']
        
    num_clients = len(clients)
    num_classes = len(class_names)
    
    matrix = np.zeros((num_clients, num_classes))
    for i, client in enumerate(clients):
        matrix[i, :] = client.class_counts
        
    fig, ax = plt.subplots(figsize=(10, 5))
    
    client_labels = [f"Hospital {i+1} (N={int(matrix[i].sum())})" for i in range(num_clients)]
    bottom = np.zeros(num_clients)
    
    colors = ['#e74c3c', '#f39c12', '#27ae60']
    
    for c in range(num_classes):
        values = matrix[:, c]
        ax.barh(client_labels, values, left=bottom, label=class_names[c], color=colors[c % len(colors)], edgecolor='black', alpha=0.85)
        
        for j in range(num_clients):
            if values[j] > 0:
                ax.text(bottom[j] + values[j] / 2, j, f"{int(values[j])}",
                        ha='center', va='center', color='white' if c == 0 else 'black',
                        fontweight='bold', fontsize=9)
        bottom += values
        
    ax.set_xlabel('Number of Patient Scans', fontsize=11, fontweight='bold')
    ax.set_title('Non-IID Pathological Distribution Across Hospital Consortia (Dirichlet Skew)', fontsize=13, fontweight='bold', pad=12)
    ax.legend(loc='lower right', framealpha=0.95, fontsize=10)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[Plot Saved] {output_path}")


def plot_confusion_matrices(results_dict, class_names=None, output_path="experiments/results/confusion_matrices.png"):
    """
    Plots side-by-side confusion matrices for all evaluated federated algorithms.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if class_names is None:
        class_names = ['IPF', 'COPD', 'Normal']
        
    methods = list(results_dict.keys())
    n_methods = len(methods)
    
    fig, axes = plt.subplots(1, n_methods, figsize=(4.5 * n_methods, 4))
    if n_methods == 1:
        axes = [axes]
        
    for idx, method in enumerate(methods):
        ax = axes[idx]
        cm = results_dict[method]['confusion_matrix']
        
        im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        ax.set_title(method, fontsize=12, fontweight='bold')
        
        tick_marks = np.arange(len(class_names))
        ax.set_xticks(tick_marks)
        ax.set_xticklabels(class_names, rotation=30, ha='right', fontsize=9)
        ax.set_yticks(tick_marks)
        ax.set_yticklabels(class_names, fontsize=9)
        
        thresh = cm.max() / 2.0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], 'd'),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black",
                        fontweight='bold', fontsize=10)
                
        ax.set_ylabel('True Label' if idx == 0 else '', fontsize=10, fontweight='bold')
        ax.set_xlabel('Predicted Label', fontsize=10, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[Plot Saved] {output_path}")

