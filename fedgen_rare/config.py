"""
Configuration and hyperparameter management for FedGen-Rare.
"""
import torch

class Config:
    def __init__(self, **kwargs):
        # Target Disease Settings
        self.disease_target = kwargs.get('disease_target', 'Idiopathic Pulmonary Fibrosis (IPF)')
        self.dataset_name = kwargs.get('dataset_name', 'ipf_chest_ct')
        self.rare_class_idx = kwargs.get('rare_class_idx', 0)
        self.num_classes = kwargs.get('num_classes', 3)
        self.class_names = kwargs.get('class_names', ['Idiopathic Pulmonary Fibrosis (Rare)', 'Common ILD / COPD', 'Normal Lung'])
        
        # Federated Consortium Settings
        self.num_clients = kwargs.get('num_clients', 5)
        self.non_iid_alpha = kwargs.get('non_iid_alpha', 0.3)  # Low alpha = severe non-IID skew
        self.global_rounds = kwargs.get('global_rounds', 20)
        self.local_epochs = kwargs.get('local_epochs', 2)
        self.batch_size = kwargs.get('batch_size', 16)
        
        # Optimization
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.seed = kwargs.get('seed', 42)
        self.lr_classifier = kwargs.get('lr_classifier', 1e-3)
        self.lr_generator = kwargs.get('lr_generator', 1e-3)
        self.weight_decay = kwargs.get('weight_decay', 1e-4)
        
        # Model Architectures
        self.classifier_backbone = kwargs.get('classifier_backbone', 'resnet18')  # 'resnet18', 'convnet', 'efficientnet'
        self.feature_dim = kwargs.get('feature_dim', 128)
        self.noise_dim = kwargs.get('noise_dim', 64)
        self.generator_hidden = kwargs.get('generator_hidden', [128, 256])
        
        # Generative Replay Hyperparameters
        self.enable_generative_replay = kwargs.get('enable_generative_replay', True)
        self.replay_ratio = kwargs.get('replay_ratio', 0.5)  # Ratio of synthetic to real in batch
        self.generator_rounds_per_global = kwargs.get('generator_rounds_per_global', 3)
        self.diversity_loss_weight = kwargs.get('diversity_loss_weight', 0.1)
        
        # FedProx baseline hyperparameter
        self.mu_prox = kwargs.get('mu_prox', 0.01)
        
        # Logging & Checkpointing
        self.output_dir = kwargs.get('output_dir', './experiments/results')
        self.verbose = kwargs.get('verbose', True)

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('__')}
