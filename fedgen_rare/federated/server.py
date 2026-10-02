"""
Federated Server coordinating global aggregation and two-stage generative replay pipeline.
"""
import copy
import numpy as np
import torch
from torch.utils.data import DataLoader

from models.classifier import build_classifier
from models.generator import ConditionalFeatureGenerator
from utils.metrics import evaluate_classifier

class FederatedServer:
    def __init__(self, clients, test_dataset, config):
        self.clients = clients
        self.test_dataset = test_dataset
        self.config = config
        self.device = config.device
        
        self.test_loader = DataLoader(
            test_dataset, batch_size=config.batch_size, shuffle=False
        )
        
        self.global_classifier = build_classifier(
            backbone=config.classifier_backbone,
            in_channels=1,
            num_classes=config.num_classes,
            feature_dim=config.feature_dim
        ).to(self.device)
        
        self.global_generator = ConditionalFeatureGenerator(
            num_classes=config.num_classes,
            noise_dim=config.noise_dim,
            feature_dim=config.feature_dim,
            hidden_dims=config.generator_hidden
        ).to(self.device)
        
        self.total_samples = sum([c.total_samples for c in self.clients])
        self.client_weights = [c.total_samples / self.total_samples for c in self.clients]
        
    def aggregate_weights(self, client_weights_list):
        avg_weights = copy.deepcopy(client_weights_list[0])
        for key in avg_weights.keys():
            avg_weights[key] = avg_weights[key] * self.client_weights[0]
            for i in range(1, len(client_weights_list)):
                avg_weights[key] += client_weights_list[i][key] * self.client_weights[i]
        return avg_weights

    def evaluate_global(self):
        return evaluate_classifier(
            self.global_classifier,
            self.test_loader,
            device=self.device,
            rare_class_idx=self.config.rare_class_idx,
            num_classes=self.config.num_classes
        )

    def train_round_fedavg(self):
        local_weights = []
        local_losses = []
        for client in self.clients:
            local_model = copy.deepcopy(self.global_classifier)
            w, loss = client.train_classifier_standard(local_model)
            local_weights.append(w)
            local_losses.append(loss)
            
        w_glob = self.aggregate_weights(local_weights)
        self.global_classifier.load_state_dict(w_glob)
        return float(np.mean(local_losses))

    def train_round_fedprox(self):
        local_weights = []
        local_losses = []
        for client in self.clients:
            local_model = copy.deepcopy(self.global_classifier)
            w, loss = client.train_classifier_standard(
                local_model, global_model=self.global_classifier, mu_prox=self.config.mu_prox
            )
            local_weights.append(w)
            local_losses.append(loss)
            
        w_glob = self.aggregate_weights(local_weights)
        self.global_classifier.load_state_dict(w_glob)
        return float(np.mean(local_losses))

    def train_round_fediic(self):
        local_weights = []
        local_losses = []
        for client in self.clients:
            local_model = copy.deepcopy(self.global_classifier)
            w, loss = client.train_classifier_fediic(local_model, k1=self.config.k1_contrastive)
            local_weights.append(w)
            local_losses.append(loss)

        w_glob = self.aggregate_weights(local_weights)
        self.global_classifier.load_state_dict(w_glob)
        return float(np.mean(local_losses))

    def train_round_fedgen_rare(self):
        # Step 1: Update the federated generator across hospital nodes
        gen_local_weights = []
        for client in self.clients:
            local_gen = copy.deepcopy(self.global_generator)
            w_gen, _ = client.train_generator_locally(
                local_gen, self.global_classifier, steps=self.config.generator_rounds_per_global
            )
            gen_local_weights.append(w_gen)
            
        w_gen_glob = self.aggregate_weights(gen_local_weights)
        self.global_generator.load_state_dict(w_gen_glob)

        # Step 2: Update diagnostic classifiers locally with Generative Replay
        clf_local_weights = []
        clf_losses = []
        for client in self.clients:
            local_model = copy.deepcopy(self.global_classifier)
            w_clf, loss = client.train_classifier_with_replay(
                local_model, self.global_generator
            )
            clf_local_weights.append(w_clf)
            clf_losses.append(loss)

        # Step 3: Aggregate diagnostic classifiers
        w_clf_glob = self.aggregate_weights(clf_local_weights)
        self.global_classifier.load_state_dict(w_clf_glob)

        return float(np.mean(clf_losses))

