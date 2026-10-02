"""
Hospital Client implementation supporting Standard Local Update, FedIIC, and Generative Rebalanced Training.
"""
import copy
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from federated.baselines import DeviceAgnosticDALA, ContrastiveAlignmentLoss

class HospitalClient:
    """
    Simulates an independent hospital node holding private, non-IID diagnostic data.
    """
    def __init__(self, client_id, dataset, config):
        self.client_id = client_id
        self.dataset = dataset
        self.config = config
        self.device = config.device
        
        self.class_counts = dataset.get_class_counts(num_classes=config.num_classes)
        self.total_samples = len(dataset)
        self.rare_samples = self.class_counts[config.rare_class_idx]
        
        self.dataloader = DataLoader(
            dataset, batch_size=config.batch_size, shuffle=True, drop_last=False
        )
        
        self.ce_criterion = nn.CrossEntropyLoss()

    def train_classifier_standard(self, model, global_model=None, mu_prox=0.0):
        """
        Standard local training for FedAvg and FedProx.
        """
        model.train()
        model.to(self.device)
        if global_model is not None:
            global_model.to(self.device)
            global_model.eval()

        optimizer = torch.optim.Adam(
            model.parameters(), lr=self.config.lr_classifier, weight_decay=self.config.weight_decay
        )

        epoch_losses = []
        for epoch in range(self.config.local_epochs):
            batch_losses = []
            for images, labels in self.dataloader:
                images, labels = images.to(self.device), labels.to(self.device)

                _, logits = model(images)
                loss = self.ce_criterion(logits, labels)

                if mu_prox > 0.0 and global_model is not None:
                    prox_loss = 0.0
                    for w, w_t in zip(model.parameters(), global_model.parameters()):
                        prox_loss += torch.norm(w - w_t) ** 2
                    loss += (mu_prox / 2.0) * prox_loss

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                batch_losses.append(loss.item())
            epoch_losses.append(np.mean(batch_losses) if batch_losses else 0.0)

        return model.state_dict(), float(np.mean(epoch_losses))

    def train_classifier_fediic(self, model, k1=1.0):
        """
        FedIIC local update using Dynamic Adaptive Logit Adjustment (DALA)
        and intra-client contrastive learning.
        """
        model.train()
        model.to(self.device)

        optimizer = torch.optim.Adam(
            model.parameters(), lr=self.config.lr_classifier, weight_decay=self.config.weight_decay
        )

        dala_criterion = DeviceAgnosticDALA(
            cls_num_list=self.class_counts, device=self.device
        )
        contrastive_criterion = ContrastiveAlignmentLoss()

        epoch_losses = []
        for epoch in range(self.config.local_epochs):
            batch_losses = []
            for images, labels in self.dataloader:
                images, labels = images.to(self.device), labels.to(self.device)

                features, logits = model(images, project=True)
                loss_ce = dala_criterion(logits, labels)
                loss_contrastive = contrastive_criterion(features, labels)

                loss = loss_ce + k1 * loss_contrastive

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                batch_losses.append(loss.item())
            epoch_losses.append(np.mean(batch_losses) if batch_losses else 0.0)

        return model.state_dict(), float(np.mean(epoch_losses))

    def train_classifier_with_replay(self, model, generator):
        """
        FedGen-Rare Local Training:
        Uses the global generator to synthesize latent features for underrepresented classes
        (specifically the rare disease), dynamically rebalancing the local optimization landscape.
        """
        model.train()
        model.to(self.device)
        generator.eval()
        generator.to(self.device)

        optimizer = torch.optim.Adam(
            model.parameters(), lr=self.config.lr_classifier, weight_decay=self.config.weight_decay
        )

        rare_idx = self.config.rare_class_idx
        num_classes = self.config.num_classes

        epoch_losses = []
        for epoch in range(self.config.local_epochs):
            batch_losses = []
            for images, labels in self.dataloader:
                images, labels = images.to(self.device), labels.to(self.device)

                real_features = model.extract_features(images)

                num_rare_in_batch = (labels == rare_idx).sum().item()
                target_synthetic = max(2, (len(labels) // num_classes) - num_rare_in_batch)

                if target_synthetic > 0 and self.config.enable_generative_replay:
                    syn_labels = torch.full((target_synthetic,), rare_idx, dtype=torch.long, device=self.device)
                    syn_features = generator.sample(syn_labels, device=self.device)

                    combined_features = torch.cat([real_features, syn_features], dim=0)
                    combined_labels = torch.cat([labels, syn_labels], dim=0)
                else:
                    combined_features = real_features
                    combined_labels = labels

                logits = model.forward_head(combined_features)
                loss = self.ce_criterion(logits, combined_labels)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                batch_losses.append(loss.item())

            epoch_losses.append(np.mean(batch_losses) if batch_losses else 0.0)

        return model.state_dict(), float(np.mean(epoch_losses))

    def train_generator_locally(self, generator, global_classifier, steps=5):
        """
        Trains the local instance of the generator using knowledge distilled
        from the global classifier and local real feature centroids (when available),
        prioritizing rare pathology feature synthesis.
        """
        generator.train()
        generator.to(self.device)
        global_classifier.eval()
        global_classifier.to(self.device)

        gen_optimizer = torch.optim.Adam(
            generator.parameters(), lr=self.config.lr_generator, weight_decay=1e-4
        )

        # Precompute local real feature centroids if available
        real_centroids = {}
        with torch.no_grad():
            for images, labels in self.dataloader:
                images, labels = images.to(self.device), labels.to(self.device)
                feats = global_classifier.extract_features(images)
                for c in range(self.config.num_classes):
                    c_mask = (labels == c)
                    if c_mask.sum() > 0:
                        if c not in real_centroids:
                            real_centroids[c] = []
                        real_centroids[c].append(feats[c_mask].mean(dim=0))
            for c in list(real_centroids.keys()):
                real_centroids[c] = torch.stack(real_centroids[c]).mean(dim=0)

        gen_losses = []
        batch_size = self.config.batch_size
        rare_idx = self.config.rare_class_idx

        for _ in range(steps):
            # Prioritize rare class generation (50% rare class, 50% uniformly sampled)
            half_b = batch_size // 2
            rare_labels = torch.full((half_b,), rare_idx, dtype=torch.long, device=self.device)
            other_labels = torch.randint(0, self.config.num_classes, (batch_size - half_b,), device=self.device)
            target_labels = torch.cat([rare_labels, other_labels], dim=0)

            noise = torch.randn(batch_size, self.config.noise_dim, device=self.device)
            gen_features = generator(noise, target_labels)

            with torch.set_grad_enabled(True):
                logits = global_classifier.forward_head(gen_features)
                loss_ce = self.ce_criterion(logits, target_labels)

                # Feature matching loss to ground generator in real clinical representations
                loss_fm = torch.tensor(0.0, device=self.device)
                matched = 0
                for c, centroid in real_centroids.items():
                    c_mask = (target_labels == c)
                    if c_mask.sum() > 0:
                        loss_fm += F.mse_loss(gen_features[c_mask].mean(dim=0), centroid)
                        matched += 1
                if matched > 0:
                    loss_fm = loss_fm / matched

                f_diff = torch.mean(torch.abs(gen_features[0::2] - gen_features[1::2]))
                z_diff = torch.mean(torch.abs(noise[0::2] - noise[1::2])) + 1e-5
                loss_div = - (f_diff / z_diff)

                loss = loss_ce + 0.3 * loss_fm + self.config.diversity_loss_weight * loss_div

            gen_optimizer.zero_grad()
            loss.backward()
            gen_optimizer.step()

            gen_losses.append(loss.item())

        return generator.state_dict(), float(np.mean(gen_losses))

