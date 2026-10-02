"""
Idiopathic Pulmonary Fibrosis (IPF) Dataset Loader with Multi-Center Non-IID Partitioning.
Incorporates realistic CT lung parenchyma physics, visual pathology overlap, and scanner domain shifts.
"""
import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

class IPFChestCTDataset(Dataset):
    """
    Dataset representing High-Resolution Computed Tomography (HRCT) slices:
    - Class 0: Idiopathic Pulmonary Fibrosis (IPF) [Rare Target Disease, ~8%]
    - Class 1: Common ILD / COPD / Emphysema [Common Pulmonary Pathology, ~42%]
    - Class 2: Normal Lung Parenchyma [Healthy Control, ~50%]
    """
    def __init__(self, images, labels, scanner_ids=None, transform=None):
        self.images = torch.tensor(images, dtype=torch.float32)
        if self.images.ndim == 3:
            self.images = self.images.unsqueeze(1)  # [N, 1, H, W]
        self.labels = torch.tensor(labels, dtype=torch.long)
        self.scanner_ids = scanner_ids
        self.transform = transform
        self.num_classes = len(torch.unique(self.labels))

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        img = self.images[idx]
        label = self.labels[idx]
        if self.transform:
            img = self.transform(img)
        return img, label

    def get_class_counts(self, num_classes=3):
        counts = [0] * num_classes
        for l in self.labels:
            counts[l.item()] += 1
        return counts


def generate_synthetic_ipf_benchmark(num_samples=1000, img_size=64, seed=42):
    """
    Generates a clinically realistic pulmonary HRCT dataset with:
    1. Identical baseline attenuation (mean HU = 0.25, std = 0.08) to avoid trivial intensity cues.
    2. Overlapping pathology signatures:
       - Class 0 (IPF): Subpleural peripheral honeycombing, irregular reticular interlobular lines,
         and traction bronchiectasis. High structural irregularity near lung periphery.
       - Class 1 (Common ILD / COPD): Diffuse ground-glass opacities (GGO), centrilobular emphysema,
         and uniform bronchial wall thickening distributed across the whole parenchyma.
       - Class 2 (Normal): Clean parenchyma with smooth tapering broncho-vascular branching.
    3. Multi-center scanner noise and contrast variations (Scanner domain shifts).
    """
    np.random.seed(seed)
    
    num_ipf = int(num_samples * 0.08)      # 8% Rare Disease
    num_copd = int(num_samples * 0.42)     # 42% Common Pathology
    num_normal = num_samples - num_ipf - num_copd  # 50% Normal
    
    images = []
    labels = []
    
    y, x = np.ogrid[:img_size, :img_size]
    # Anatomical lung field mask (bilateral thoracic oval shape)
    left_lung = ((x - img_size*0.32)**2 / (img_size*0.22)**2 + (y - img_size*0.5)**2 / (img_size*0.4)**2) < 1.0
    right_lung = ((x - img_size*0.68)**2 / (img_size*0.22)**2 + (y - img_size*0.5)**2 / (img_size*0.4)**2) < 1.0
    lung_mask = left_lung | right_lung
    
    # 1. Normal Lungs (50%)
    for _ in range(num_normal):
        # Baseline parenchymal background
        img = np.random.normal(loc=0.25, scale=0.04, size=(img_size, img_size))
        # Smooth broncho-vascular arborization
        vessels = np.exp(-((x - img_size*0.5)**2 + (y - img_size*0.5)**2) / (img_size * 2.5)) * 0.15
        img = (img + vessels) * lung_mask
        # Sensor acquisition noise
        img += np.random.normal(loc=0.0, scale=0.03, size=(img_size, img_size)) * lung_mask
        images.append(img)
        labels.append(2)
        
    # 2. Common ILD / COPD (42%)
    for _ in range(num_copd):
        img = np.random.normal(loc=0.25, scale=0.04, size=(img_size, img_size))
        # Diffuse non-specific ground-glass opacities (overlapping low-frequency texture)
        ggo = (np.sin(x / 4.0) * np.cos(y / 4.0) + np.sin(x / 7.0)) * 0.08
        # Centrilobular emphysema micro-lucent spots
        emphysema = (np.random.rand(img_size, img_size) > 0.88).astype(np.float32) * -0.1
        img = (img + ggo + emphysema) * lung_mask
        img += np.random.normal(loc=0.0, scale=0.035, size=(img_size, img_size)) * lung_mask
        images.append(img)
        labels.append(1)
        
    # 3. Idiopathic Pulmonary Fibrosis (Rare Target, 8%)
    for _ in range(num_ipf):
        img = np.random.normal(loc=0.25, scale=0.04, size=(img_size, img_size))
        # Shared ground-glass background (creates real clinical diagnostic dilemma)
        ggo = (np.sin(x / 4.0) * np.cos(y / 4.0)) * 0.06
        # Hallmark IPF: Subpleural peripheral honeycombing cysts (cysts surrounded by thick fibrotic walls)
        peripheral_subpleural = lung_mask & ~(((x - img_size*0.32)**2 / (img_size*0.13)**2 + (y - img_size*0.5)**2 / (img_size*0.25)**2 < 1.0) |
                                              ((x - img_size*0.68)**2 / (img_size*0.13)**2 + (y - img_size*0.5)**2 / (img_size*0.25)**2 < 1.0))
        honeycomb_clusters = (np.random.rand(img_size, img_size) > 0.65).astype(np.float32) * 0.22
        # Traction bronchiectasis (irregular dilated tubular structures)
        bronchiectasis = (np.abs(np.sin(x / 3.0 + y / 3.0)) < 0.25).astype(np.float32) * 0.12 * peripheral_subpleural
        
        img = (img + ggo + honeycomb_clusters * peripheral_subpleural + bronchiectasis) * lung_mask
        img += np.random.normal(loc=0.0, scale=0.04, size=(img_size, img_size)) * lung_mask
        images.append(img)
        labels.append(0)
        
    images = np.array(images, dtype=np.float32)
    labels = np.array(labels, dtype=np.int64)
    
    perm = np.random.permutation(len(labels))
    images = images[perm]
    labels = labels[perm]
    
    return images, labels


def partition_multi_center_non_iid(dataset, num_clients=5, alpha=0.2, seed=42):
    """
    Partitions dataset across hospital silos using Dirichlet distribution to simulate:
    - Extreme non-IID label skew (alpha=0.2 yields high sparsity for the rare class).
    - Hospital 1 may hold ~15 IPF cases, while Hospital 2 has only 1 case, and Hospital 3 has 0 cases.
    - Applies realistic inter-hospital CT scanner domain shifts (simulating Siemens, GE, Philips hardware).
    """
    np.random.seed(seed)
    labels = dataset.labels.numpy()
    num_classes = len(np.unique(labels))
    
    client_indices = {i: [] for i in range(num_clients)}
    
    for c in range(num_classes):
        idx_c = np.where(labels == c)[0]
        np.random.shuffle(idx_c)
        
        proportions = np.random.dirichlet(np.repeat(alpha, num_clients))
        proportions = proportions / proportions.sum()
        
        splits = (np.cumsum(proportions) * len(idx_c)).astype(int)[:-1]
        client_subsets = np.split(idx_c, splits)
        
        for i in range(num_clients):
            client_indices[i].extend(client_subsets[i].tolist())
            
    # Scanner hardware noise shifts per hospital (simulating multi-vendor CT fleets)
    scanner_noise_profiles = [0.01, 0.03, 0.05, 0.02, 0.04]
    scanner_contrast_scales = [1.05, 0.95, 1.10, 0.90, 1.00]
    
    client_datasets = []
    for i in range(num_clients):
        sub_idx = np.array(client_indices[i])
        np.random.shuffle(sub_idx)
        sub_images = dataset.images[sub_idx].numpy().copy()
        sub_labels = dataset.labels[sub_idx].numpy().copy()
        
        # Apply inter-hospital CT scanner domain shift
        sub_images = sub_images * scanner_contrast_scales[i % len(scanner_contrast_scales)]
        sub_images += np.random.normal(0, scanner_noise_profiles[i % len(scanner_noise_profiles)], size=sub_images.shape)
        sub_images = np.clip(sub_images, 0.0, 1.0)
        
        client_datasets.append(IPFChestCTDataset(sub_images, sub_labels, scanner_ids=i))
        
    return client_datasets


def get_ipf_federated_environment(num_clients=5, alpha=0.2, num_samples=1200, test_ratio=0.25, seed=42):
    """
    Sets up the full federated learning environment:
    - Distributed client datasets (heterogeneous hospital silos)
    - Global held-out test set
    """
    images, labels = generate_synthetic_ipf_benchmark(num_samples=num_samples, seed=seed)
    
    split_idx = int(len(labels) * (1 - test_ratio))
    train_images, test_images = images[:split_idx], images[split_idx:]
    train_labels, test_labels = labels[:split_idx], labels[split_idx:]
    
    train_global_dataset = IPFChestCTDataset(train_images, train_labels)
    test_global_dataset = IPFChestCTDataset(test_images, test_labels)
    
    client_datasets = partition_multi_center_non_iid(
        train_global_dataset, num_clients=num_clients, alpha=alpha, seed=seed
    )
    
    return client_datasets, test_global_dataset

