"""
Baseline implementations: FedIIC (MICCAI '23) adapter and contrastive alignment.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

class DeviceAgnosticDALA(nn.Module):
    """
    Dynamic Adaptive Logit Adjustment (DALA) from FedIIC (MICCAI '23).
    Adjusts classification margins based on class prior frequencies and training difficulty.
    """
    def __init__(self, cls_num_list, cls_loss=None, tau=1.0, d=0.25, device='cpu'):
        super(DeviceAgnosticDALA, self).__init__()
        cls_num_tensor = torch.tensor(cls_num_list, dtype=torch.float32, device=device)
        cls_p_list = cls_num_tensor / (cls_num_tensor.sum() + 1e-8)
        
        if cls_loss is None:
            cls_loss = torch.ones(len(cls_num_list), device=device)
        else:
            cls_loss = cls_loss.to(device)
            
        t = cls_p_list / (torch.pow(cls_loss, d) + 1e-5)
        m_list = tau * torch.log(t + 1e-8)
        self.m_list = m_list.view(1, -1)

    def forward(self, logits, target):
        adjusted_logits = logits + self.m_list
        return F.cross_entropy(adjusted_logits, target)


class ContrastiveAlignmentLoss(nn.Module):
    """
    Normalized Temperature-scaled Cross Entropy (NT-Xent) contrastive loss
    for feature alignment between representations.
    """
    def __init__(self, temperature=0.1):
        super(ContrastiveAlignmentLoss, self).__init__()
        self.temperature = temperature

    def forward(self, features, labels):
        device = features.device
        norm_features = F.normalize(features, dim=1)
        sim_matrix = torch.matmul(norm_features, norm_features.T) / self.temperature
        
        # Mask out self-similarity
        mask = torch.eye(features.size(0), dtype=torch.bool, device=device)
        sim_matrix.masked_fill_(mask, -1e9)
        
        # Label match matrix
        labels = labels.contiguous().view(-1, 1)
        pos_mask = torch.eq(labels, labels.T) & ~mask
        
        if pos_mask.sum() == 0:
            return torch.tensor(0.0, device=device)
            
        exp_sim = torch.exp(sim_matrix)
        log_prob = sim_matrix - torch.log(exp_sim.sum(dim=1, keepdim=True) + 1e-8)
        
        mean_log_prob = (pos_mask * log_prob).sum(dim=1) / (pos_mask.sum(dim=1) + 1e-8)
        loss = -mean_log_prob.mean()
        return loss

