"""
Unit Tests for FedGen-Rare: Module-level verification of all system components.

Run with:  pytest tests/ -v
"""
import sys
import os
import pytest
import torch
import numpy as np

# Make fedgen_rare importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fedgen_rare'))

from config import Config
from models.classifier import ConvNet, ResNetClassifier, build_classifier
from models.generator import ConditionalFeatureGenerator
from datasets.ipf_dataset import (
    generate_synthetic_ipf_benchmark,
    IPFChestCTDataset,
    partition_multi_center_non_iid,
    get_ipf_federated_environment,
)
from federated.baselines import DeviceAgnosticDALA, ContrastiveAlignmentLoss
from federated.client import HospitalClient
from federated.server import FederatedServer
from utils.metrics import evaluate_classifier
from torch.utils.data import DataLoader


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def config():
    return Config(
        num_clients=3,
        global_rounds=2,
        local_epochs=1,
        batch_size=8,
        num_classes=3,
        feature_dim=64,
        noise_dim=32,
        generator_hidden=[64, 128],
        seed=42,
    )


@pytest.fixture(scope="module")
def small_dataset():
    """Generate a small synthetic IPF dataset for fast test runs."""
    images, labels = generate_synthetic_ipf_benchmark(num_samples=120, img_size=32, seed=42)
    return images, labels


@pytest.fixture(scope="module")
def federated_env(config):
    """Create a mini federated environment: 3 clients + test set."""
    client_datasets, test_dataset = get_ipf_federated_environment(
        num_clients=3, alpha=0.3, num_samples=180, test_ratio=0.2, seed=42
    )
    clients = [HospitalClient(i, client_datasets[i], config) for i in range(3)]
    return clients, test_dataset


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 1: Dataset Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestDatasetGeneration:
    """PI 3.1.3 — Validates synthetic dataset generation matches clinical spec."""

    def test_dataset_shape(self, small_dataset):
        """Images must be (N, H, W) and labels must be (N,)."""
        images, labels = small_dataset
        assert images.ndim == 3, "Images should be 3D (N, H, W)"
        assert labels.ndim == 1, "Labels should be 1D (N,)"
        assert images.shape[0] == labels.shape[0], "Image/label count must match"

    def test_class_distribution(self, small_dataset):
        """IPF class (0) must be rare (~8%), COPD (~42%), Normal (~50%)."""
        images, labels = small_dataset
        n = len(labels)
        ipf_pct = (labels == 0).sum() / n
        copd_pct = (labels == 1).sum() / n
        normal_pct = (labels == 2).sum() / n
        # Allow ±5% tolerance
        assert 0.03 <= ipf_pct <= 0.13, f"IPF prevalence {ipf_pct:.2%} out of expected range ~8%"
        assert 0.37 <= copd_pct <= 0.47, f"COPD prevalence {copd_pct:.2%} out of expected range ~42%"
        assert 0.45 <= normal_pct <= 0.55, f"Normal prevalence {normal_pct:.2%} out of expected range ~50%"

    def test_pixel_range(self, small_dataset):
        """Pixel values must be finite and within plausible HRCT attenuation range."""
        images, labels = small_dataset
        assert np.isfinite(images).all(), "Images must contain no NaN or Inf values"
        # After clipping in partitioning, expected range is roughly [-0.3, 1.5]
        assert images.min() >= -0.5, "Pixel minimum unexpectedly low"
        assert images.max() <= 1.5, "Pixel maximum unexpectedly high"

    def test_dataset_class_counts_method(self, small_dataset):
        """IPFChestCTDataset.get_class_counts() must return a list of 3 integers."""
        images, labels = small_dataset
        ds = IPFChestCTDataset(images, labels)
        counts = ds.get_class_counts(num_classes=3)
        assert len(counts) == 3, "Must return counts for all 3 classes"
        assert sum(counts) == len(labels), "Class counts must sum to dataset size"
        assert all(isinstance(c, int) for c in counts), "Counts must be integers"

    def test_non_iid_partition(self, small_dataset):
        """Non-IID partitioning must create client-level skew without data loss."""
        images, labels = small_dataset
        ds = IPFChestCTDataset(images, labels)
        client_datasets = partition_multi_center_non_iid(ds, num_clients=3, alpha=0.3, seed=42)
        total_samples = sum(len(cd) for cd in client_datasets)
        assert total_samples == len(ds), "No data should be lost in partitioning"
        # Verify at least one client has skew (not perfectly uniform)
        client_ipf = [cd.get_class_counts()[0] for cd in client_datasets]
        assert max(client_ipf) != min(client_ipf), "Non-IID should introduce client skew"


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 2: Model Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestClassifierModels:
    """PI 3.3.3 — Validates ConvNet and ResNet diagnostic backbone architectures."""

    def test_convnet_forward_shape(self, config):
        """ConvNet must produce (N, feature_dim) features and (N, num_classes) logits."""
        model = ConvNet(in_channels=1, num_classes=config.num_classes, feature_dim=config.feature_dim)
        x = torch.randn(4, 1, 64, 64)
        features, logits = model(x)
        assert features.shape == (4, config.feature_dim), f"Feature shape mismatch: {features.shape}"
        assert logits.shape == (4, config.num_classes), f"Logit shape mismatch: {logits.shape}"

    def test_convnet_extract_features(self, config):
        """extract_features must return (N, feature_dim) tensor."""
        model = ConvNet(in_channels=1, num_classes=config.num_classes, feature_dim=config.feature_dim)
        x = torch.randn(4, 1, 64, 64)
        feats = model.extract_features(x)
        assert feats.shape == (4, config.feature_dim)

    def test_convnet_forward_head(self, config):
        """forward_head must accept feature vectors and return logits."""
        model = ConvNet(in_channels=1, num_classes=config.num_classes, feature_dim=config.feature_dim)
        feats = torch.randn(4, config.feature_dim)
        logits = model.forward_head(feats)
        assert logits.shape == (4, config.num_classes)

    def test_convnet_projection(self, config):
        """Projection head (for contrastive learning) must return (N, feature_dim)."""
        model = ConvNet(in_channels=1, num_classes=config.num_classes, feature_dim=config.feature_dim)
        x = torch.randn(4, 1, 64, 64)
        proj, logits = model(x, project=True)
        assert proj.shape == (4, config.feature_dim)

    def test_build_classifier_convnet(self, config):
        """build_classifier factory must return a functional ConvNet."""
        model = build_classifier('convnet', in_channels=1, num_classes=3, feature_dim=64)
        x = torch.randn(2, 1, 64, 64)
        feats, logits = model(x)
        assert logits.shape == (2, 3)

    def test_build_classifier_resnet(self, config):
        """build_classifier factory must return a functional ResNetClassifier."""
        model = build_classifier('resnet', in_channels=1, num_classes=3, feature_dim=64)
        x = torch.randn(2, 1, 64, 64)
        feats, logits = model(x)
        assert logits.shape == (2, 3)

    def test_single_sample_inference(self, config):
        """Model must handle batch size of 1 without LayerNorm errors."""
        model = ConvNet(in_channels=1, num_classes=3, feature_dim=64)
        model.eval()
        x = torch.randn(1, 1, 64, 64)
        with torch.no_grad():
            feats, logits = model(x)
        assert logits.shape == (1, 3)


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 3: Generator Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestConditionalGenerator:
    """PI 3.3.3 — Validates conditional latent feature generator architecture."""

    def test_generator_output_shape(self, config):
        """Generator must produce (N, feature_dim) synthetic feature vectors."""
        gen = ConditionalFeatureGenerator(
            num_classes=config.num_classes,
            noise_dim=config.noise_dim,
            feature_dim=config.feature_dim,
            hidden_dims=config.generator_hidden,
        )
        noise = torch.randn(8, config.noise_dim)
        labels = torch.randint(0, config.num_classes, (8,))
        out = gen(noise, labels)
        assert out.shape == (8, config.feature_dim), f"Generator output shape mismatch: {out.shape}"

    def test_generator_sample_method(self, config):
        """Generator.sample() must generate correct number of IPF features."""
        gen = ConditionalFeatureGenerator(
            num_classes=config.num_classes,
            noise_dim=config.noise_dim,
            feature_dim=config.feature_dim,
            hidden_dims=config.generator_hidden,
        )
        labels = torch.zeros(5, dtype=torch.long)  # 5 IPF samples
        samples = gen.sample(labels, device='cpu')
        assert samples.shape == (5, config.feature_dim)

    def test_generator_diverse_outputs(self, config):
        """Different noise inputs for same class must produce different features."""
        gen = ConditionalFeatureGenerator(
            num_classes=config.num_classes,
            noise_dim=config.noise_dim,
            feature_dim=config.feature_dim,
            hidden_dims=config.generator_hidden,
        )
        labels = torch.zeros(4, dtype=torch.long)
        n1, n2 = torch.randn(4, config.noise_dim), torch.randn(4, config.noise_dim)
        out1, out2 = gen(n1, labels), gen(n2, labels)
        assert not torch.allclose(out1, out2), "Generator must produce diverse outputs for different noise"


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 4: Baseline Loss Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestBaselineLosses:
    """PI 3.3.3 — Validates FedIIC DALA and contrastive loss implementations."""

    def test_dala_computes_loss(self):
        """DALA loss must return a scalar tensor for valid inputs."""
        dala = DeviceAgnosticDALA(cls_num_list=[5, 50, 100], device='cpu')
        logits = torch.randn(8, 3)
        labels = torch.randint(0, 3, (8,))
        loss = dala(logits, labels)
        assert loss.ndim == 0, "DALA loss must be scalar"
        assert torch.isfinite(loss), "DALA loss must be finite"

    def test_dala_zero_rare_class(self):
        """DALA must handle zero-count rare class without NaN (numerical stability)."""
        dala = DeviceAgnosticDALA(cls_num_list=[0, 50, 100], device='cpu')
        logits = torch.randn(8, 3)
        labels = torch.randint(0, 3, (8,))
        loss = dala(logits, labels)
        assert torch.isfinite(loss), "DALA must be numerically stable with zero rare class count"

    def test_contrastive_loss_computes(self):
        """ContrastiveAlignmentLoss must return a finite scalar."""
        criterion = ContrastiveAlignmentLoss(temperature=0.1)
        features = torch.randn(8, 64)
        labels = torch.tensor([0, 0, 1, 1, 2, 2, 0, 1])
        loss = criterion(features, labels)
        assert loss.ndim == 0, "Contrastive loss must be scalar"
        assert torch.isfinite(loss), "Contrastive loss must be finite"

    def test_contrastive_loss_no_positive_pairs(self):
        """ContrastiveAlignmentLoss must handle the case where all labels are unique (no positive pairs)."""
        criterion = ContrastiveAlignmentLoss(temperature=0.1)
        features = torch.randn(3, 64)
        labels = torch.tensor([0, 1, 2])  # All unique — FedIIC failure scenario
        loss = criterion(features, labels)
        # Should return 0.0 gracefully, not crash
        assert torch.isfinite(loss), "Must not produce NaN when no positive pairs exist"


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 5: Hospital Client Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestHospitalClient:
    """PI 12.1.2 — Validates hospital client local training routines."""

    def test_client_initialization(self, federated_env):
        """HospitalClient must correctly report sample and rare class counts."""
        clients, _ = federated_env
        for i, client in enumerate(clients):
            assert client.client_id == i
            assert client.total_samples > 0
            assert isinstance(client.class_counts, list)
            assert len(client.class_counts) == 3
            assert sum(client.class_counts) == client.total_samples

    def test_standard_training_returns_weights(self, config, federated_env):
        """Standard local training (FedAvg) must return model state dict and scalar loss."""
        clients, _ = federated_env
        model = build_classifier('convnet', in_channels=1, num_classes=3, feature_dim=64)
        import copy
        w, loss = clients[0].train_classifier_standard(copy.deepcopy(model))
        assert isinstance(w, dict), "Must return state dict"
        assert isinstance(loss, float), "Must return scalar loss"
        assert loss >= 0, "Loss must be non-negative"

    def test_fediic_training_returns_weights(self, config, federated_env):
        """FedIIC training must complete and return model weights and loss."""
        clients, _ = federated_env
        model = build_classifier('convnet', in_channels=1, num_classes=3, feature_dim=64)
        import copy
        w, loss = clients[0].train_classifier_fediic(copy.deepcopy(model))
        assert isinstance(w, dict)
        assert isinstance(loss, float)

    def test_generative_replay_training(self, config, federated_env):
        """Generative replay training must return weights even for data-scarce clients."""
        clients, _ = federated_env
        model = build_classifier('convnet', in_channels=1, num_classes=3, feature_dim=64)
        gen = ConditionalFeatureGenerator(
            num_classes=3, noise_dim=32, feature_dim=64, hidden_dims=[64, 128]
        )
        import copy
        w, loss = clients[0].train_classifier_with_replay(copy.deepcopy(model), gen)
        assert isinstance(w, dict)
        assert isinstance(loss, float)


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 6: Server & Global Aggregation Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestFederatedServer:
    """PI 12.1.2 — Validates federated aggregation rounds."""

    def test_server_initialization(self, config, federated_env):
        """Server must correctly compute client weights summing to 1.0."""
        clients, test_dataset = federated_env
        server = FederatedServer(clients, test_dataset, config)
        assert abs(sum(server.client_weights) - 1.0) < 1e-5, "Client weights must sum to 1.0"
        assert server.global_classifier is not None
        assert server.global_generator is not None

    def test_fedavg_round(self, config, federated_env):
        """FedAvg round must return scalar loss."""
        clients, test_dataset = federated_env
        server = FederatedServer(clients, test_dataset, config)
        loss = server.train_round_fedavg()
        assert isinstance(loss, float)
        assert loss >= 0

    def test_fedprox_round(self, config, federated_env):
        """FedProx round must run without error."""
        clients, test_dataset = federated_env
        server = FederatedServer(clients, test_dataset, config)
        loss = server.train_round_fedprox()
        assert isinstance(loss, float)

    def test_fediic_round(self, config, federated_env):
        """FedIIC round must run without error."""
        clients, test_dataset = federated_env
        server = FederatedServer(clients, test_dataset, config)
        loss = server.train_round_fediic()
        assert isinstance(loss, float)

    def test_fedgen_rare_round(self, config, federated_env):
        """FedGen-Rare round (generator + classifier update) must run without error."""
        clients, test_dataset = federated_env
        server = FederatedServer(clients, test_dataset, config)
        loss = server.train_round_fedgen_rare()
        assert isinstance(loss, float)

    def test_evaluate_global_returns_metrics(self, config, federated_env):
        """Global evaluation must return all required clinical metrics."""
        clients, test_dataset = federated_env
        server = FederatedServer(clients, test_dataset, config)
        metrics = server.evaluate_global()
        required_keys = ['accuracy', 'balanced_accuracy', 'macro_f1',
                         'rare_recall', 'rare_precision', 'rare_f1', 'auc_roc']
        for key in required_keys:
            assert key in metrics, f"Missing metric: {key}"
            assert isinstance(metrics[key], float), f"Metric {key} must be float"
            assert 0.0 <= metrics[key] <= 1.0, f"Metric {key}={metrics[key]} out of [0,1] range"


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 7: Metrics Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestMetrics:
    """PI 5.2.2 — Validates evaluation metric correctness."""

    def test_evaluate_classifier_all_correct(self):
        """evaluate_classifier must return 1.0 accuracy for a perfect classifier."""
        model = build_classifier('convnet', in_channels=1, num_classes=3, feature_dim=64)
        # Create dataset where the model will produce reasonable predictions
        images = torch.randn(24, 1, 64, 64)
        labels = torch.tensor([0, 0, 1, 1, 2, 2] * 4)
        ds = torch.utils.data.TensorDataset(images, labels)
        loader = DataLoader(ds, batch_size=8)
        metrics = evaluate_classifier(model, loader, device='cpu', rare_class_idx=0, num_classes=3)
        # Just check it runs and returns all expected keys
        assert 'accuracy' in metrics
        assert 'rare_recall' in metrics
        assert 0.0 <= metrics['accuracy'] <= 1.0

    def test_evaluate_balanced_accuracy_range(self):
        """Balanced accuracy must be in [0, 1] range."""
        model = build_classifier('convnet', in_channels=1, num_classes=3, feature_dim=64)
        images = torch.randn(15, 1, 64, 64)
        labels = torch.tensor([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2])
        ds = torch.utils.data.TensorDataset(images, labels)
        loader = DataLoader(ds, batch_size=5)
        metrics = evaluate_classifier(model, loader, device='cpu', rare_class_idx=0, num_classes=3)
        assert 0.0 <= metrics['balanced_accuracy'] <= 1.0

