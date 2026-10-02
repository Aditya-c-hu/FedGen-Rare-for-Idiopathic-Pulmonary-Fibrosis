"""
Conditional Latent Feature Generator for Federated Generative Replay in Rare Disease Diagnosis.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

class ConditionalFeatureGenerator(nn.Module):
    """
    Conditional Generative Network modeling the latent distribution P(f | y = c_rare).
    Maps Gaussian noise z ~ N(0, I) and class label y to feature vector f_hat in latent space.
    """
    def __init__(self, num_classes=3, noise_dim=64, feature_dim=128, hidden_dims=[128, 256], embedding_dim=32):
        super(ConditionalFeatureGenerator, self).__init__()
        self.num_classes = num_classes
        self.noise_dim = noise_dim
        self.feature_dim = feature_dim
        self.label_embedding = nn.Embedding(num_classes, embedding_dim)
        
        input_dim = noise_dim + embedding_dim
        layers = []
        curr_dim = input_dim
        for h_dim in hidden_dims:
            layers.append(nn.Linear(curr_dim, h_dim))
            layers.append(nn.LayerNorm(h_dim))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            curr_dim = h_dim
            
        layers.append(nn.Linear(curr_dim, feature_dim))
        layers.append(nn.LayerNorm(feature_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, noise, labels):
        label_emb = self.label_embedding(labels)
        x = torch.cat([noise, label_emb], dim=1)
        features = self.net(x)
        return features

    def sample(self, labels, device='cpu'):
        self.eval()
        with torch.no_grad():
            batch_size = len(labels)
            if not isinstance(labels, torch.Tensor):
                labels = torch.tensor(labels, dtype=torch.long, device=device)
            else:
                labels = labels.to(device)
            noise = torch.randn(batch_size, self.noise_dim, device=device)
            return self.forward(noise, labels)


class GeneratorLoss(nn.Module):
    """
    Loss function for training the federated generator:
    1. Cross-entropy with classifier logits (Semantic Fidelity)
    2. Mode-seeking diversity loss to prevent mode collapse on rare diseases.
    """
    def __init__(self, diversity_weight=0.15):
        super(GeneratorLoss, self).__init__()
        self.ce = nn.CrossEntropyLoss()
        self.diversity_weight = diversity_weight

    def forward(self, logits, labels, features=None, noise=None):
        loss_ce = self.ce(logits, labels)
        
        loss_div = 0.0
        if features is not None and noise is not None and features.size(0) > 1:
            f_diff = torch.mean(torch.abs(features[0::2] - features[1::2]))
            z_diff = torch.mean(torch.abs(noise[0::2] - noise[1::2])) + 1e-5
            loss_div = - (f_diff / z_diff)
            
        total_loss = loss_ce + self.diversity_weight * loss_div
        return total_loss, loss_ce, loss_div

