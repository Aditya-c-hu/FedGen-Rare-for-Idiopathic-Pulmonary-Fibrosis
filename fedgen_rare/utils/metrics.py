"""
Evaluation metrics for federated classification with severe class imbalance and rare disease focus.
"""
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score
)

def evaluate_classifier(model, dataloader, device='cpu', rare_class_idx=0, num_classes=3):
    """
    Evaluates classifier across global test set, computing overall and rare-specific clinical metrics.
    """
    model.eval()
    model.to(device)

    all_preds = []
    all_targets = []
    all_probs = []

    with torch.no_grad():
        for images, labels in dataloader:
            images = images.to(device)
            labels = labels.to(device)

            _, logits = model(images)
            probs = F.softmax(logits, dim=1)
            preds = torch.argmax(probs, dim=1)

            all_preds.extend(preds.cpu().numpy().tolist())
            all_targets.extend(labels.cpu().numpy().tolist())
            all_probs.extend(probs.cpu().numpy().tolist())

    y_true = np.array(all_targets)
    y_pred = np.array(all_preds)
    y_prob = np.array(all_probs)

    # Standard metrics
    acc = accuracy_score(y_true, y_pred)
    bacc = balanced_accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)

    # Rare disease specific metrics (Class 0: IPF)
    rare_recall = recall_score(y_true, y_pred, labels=[rare_class_idx], average=None, zero_division=0)[0]
    rare_precision = precision_score(y_true, y_pred, labels=[rare_class_idx], average=None, zero_division=0)[0]
    rare_f1 = f1_score(y_true, y_pred, labels=[rare_class_idx], average=None, zero_division=0)[0]

    # Per-class recall
    recalls = recall_score(y_true, y_pred, average=None, zero_division=0)
    per_class_recall = {f"Class_{i}_Recall": float(recalls[i]) if i < len(recalls) else 0.0 for i in range(num_classes)}

    # Multi-class AUC if possible
    try:
        if num_classes == 2:
            auc = roc_auc_score(y_true, y_prob[:, 1])
        else:
            auc = roc_auc_score(y_true, y_prob, multi_class='ovr', average='macro')
    except Exception:
        auc = 0.0

    cm = confusion_matrix(y_true, y_pred, labels=list(range(num_classes)))

    metrics = {
        'accuracy': float(acc),
        'balanced_accuracy': float(bacc),
        'macro_f1': float(macro_f1),
        'rare_recall': float(rare_recall),
        'rare_precision': float(rare_precision),
        'rare_f1': float(rare_f1),
        'auc_roc': float(auc),
        'confusion_matrix': cm,
        'y_true': y_true,
        'y_pred': y_pred,
        'y_prob': y_prob
    }
    metrics.update(per_class_recall)
    return metrics

