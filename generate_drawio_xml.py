"""
Generate native Draw.io (.drawio) XML diagram files
for seamless drag-and-drop opening in Draw.io / diagrams.net.
Fixes geometry parsing (as="geometry"), text wrapping (html=1),
and provides spacious, beautifully aligned component layouts.
"""
import os
import xml.etree.ElementTree as ET

def create_drawio_xml(diagram_name, elements, width=1800, height=1200):
    """
    Creates a strictly valid, spacious mxGraphModel XML document for Draw.io.
    Every mxGeometry MUST have as="geometry".
    Every vertex MUST have html=1 and whiteSpace=wrap.
    """
    mxfile = ET.Element("mxfile", host="app.diagrams.net", version="21.0.0")
    diagram = ET.SubElement(mxfile, "diagram", id="diag1", name=diagram_name)
    model = ET.SubElement(
        diagram, "mxGraphModel",
        dx="1600", dy="1000", grid="1", gridSize="10",
        guides="1", tooltips="1", connect="1", arrows="1",
        fold="1", page="1", pageScale="1",
        pageWidth=str(width), pageHeight=str(height),
        math="0", shadow="0"
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    for el in elements:
        cell = ET.SubElement(root, "mxCell", id=str(el["id"]))
        cell.set("parent", str(el.get("parent", "1")))

        if el.get("edge"):
            cell.set("edge", "1")
            cell.set("source", str(el["source"]))
            cell.set("target", str(el["target"]))
            cell.set("style", el.get("style", "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#1A5FB4;strokeWidth=2;"))
            if "value" in el:
                cell.set("value", el["value"])
            geo = ET.SubElement(cell, "mxGeometry", relative="1")
            geo.set("as", "geometry")
        else:
            cell.set("vertex", "1")
            cell.set("value", el["value"])
            
            # Ensure html=1 and whiteSpace=wrap are always present for beautiful text rendering
            default_style = "rounded=1;whiteSpace=wrap;html=1;"
            style = el.get("style", default_style)
            if "html=1" not in style:
                style = style.rstrip(";") + ";html=1;"
            if "whiteSpace=wrap" not in style:
                style = style.rstrip(";") + ";whiteSpace=wrap;"
            cell.set("style", style)

            geo = ET.SubElement(
                cell, "mxGeometry",
                x=str(el["x"]), y=str(el["y"]),
                width=str(el["w"]), height=str(el["h"])
            )
            geo.set("as", "geometry")

    return ET.tostring(mxfile, encoding="utf-8", xml_declaration=True)


def generate_all_drawio():
    out_dir = "docs/uml"
    os.makedirs(out_dir, exist_ok=True)

    # ─────────────────────────────────────────────────────────────
    # 1. COMPONENT DIAGRAM (docs/uml/01_component_diagram.drawio)
    # ─────────────────────────────────────────────────────────────
    comp_elements = [
        # Top Container: Global Federated Server
        {"id": 100, "value": "<b>Global Federated Server (Trusted Central Aggregator)</b>",
         "style": "rounded=1;fillColor=#F0F4F8;strokeColor=#1A5FB4;strokeWidth=2;verticalAlign=top;align=left;spacingLeft=20;spacingTop=12;fontColor=#0A2540;fontSize=14;fontStyle=1;",
         "x": 340, "y": 40, "w": 960, "h": 240},

        {"id": 101, "value": "<b>Global Classifier (F_θ)</b><br>ResNet-18 / ConvNet Backbone<br>128-dim Latent Embeddings",
         "style": "rounded=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 370, "y": 90, "w": 260, "h": 75},

        {"id": 102, "value": "<b>Global Conditional Generator (G_ψ)</b><br>Latent Distribution Model<br>p(f | y=IPF, COPD, Normal)",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 680, "y": 90, "w": 270, "h": 75},

        {"id": 103, "value": "<b>Federated Parameter Aggregator</b><br>θ_glob = Σ (n_k/N) θ_k<br>ψ_glob = Σ (n_k/N) ψ_k",
         "style": "rounded=1;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 990, "y": 90, "w": 280, "h": 75},

        {"id": 104, "value": "<b>Federated Orchestration &amp; Evaluation Engine</b><br>Round Scheduling • Convergence Check • Multi-Center Test Evaluation (BACC, Recall, AUROC)",
         "style": "rounded=1;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 480, "y": 185, "w": 680, "h": 65},

        # Middle Container: Encrypted Network Boundary Band
        {"id": 150, "value": "<b>SECURE ENCRYPTED NETWORK BOUNDARY (Zero Raw Data Leakage — Parameters &amp; Latents Only)</b>",
         "style": "rounded=1;fillColor=#FFF8E1;strokeColor=#FFA000;strokeWidth=2;dashed=1;fontColor=#B78103;fontSize=13;fontStyle=1;align=center;",
         "x": 80, "y": 315, "w": 1480, "h": 45},

        # Hospital 1 (Tertiary Academic Center - High IPF)
        {"id": 200, "value": "<b>Hospital 1: Tertiary Medical Center</b> [Balanced, High IPF Cases]",
         "style": "rounded=1;fillColor=#F8FAFC;strokeColor=#1A5FB4;strokeWidth=2;verticalAlign=top;align=left;spacingLeft=15;spacingTop=10;fontColor=#0A2540;fontSize=13;fontStyle=1;",
         "x": 80, "y": 390, "w": 460, "h": 530},

        {"id": 201, "value": "<b>Private HRCT Dataset</b><br>33 IPF | 72 COPD | 296 Norm<br>Siemens Somatom Scanner",
         "style": "shape=cylinder3;size=15;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 105, "y": 445, "w": 200, "h": 80},

        {"id": 202, "value": "<b>Local Classifier (F_θ_1)</b><br>Extracts 128-d features<br>Computes Real Centroids",
         "style": "rounded=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 325, "y": 445, "w": 190, "h": 80},

        {"id": 203, "value": "<b>Local Generator Distillation (G_ψ_1)</b><br>Multi-Task Loss: L_CE + λ_fm L_FM - λ_div L_DIV<br>Anchored to local real IPF centroids",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 105, "y": 550, "w": 410, "h": 70},

        {"id": 204, "value": "<b>Generative Latent Replay Engine</b><br>Balances mini-batches on-the-fly<br>f_comb = Concat[f_real, f̂_IPF]",
         "style": "rounded=1;fillColor=#FFF2CC;strokeColor=#D6B656;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 105, "y": 645, "w": 410, "h": 70},

        {"id": 205, "value": "<b>Hospital 1 Federated Client Node</b><br>Receives (θ, ψ) • Computes (Δθ_1, Δψ_1) • Secure Upload",
         "style": "rounded=1;fillColor=#EBF3FB;strokeColor=#1A5FB4;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 105, "y": 740, "w": 410, "h": 65},

        # Hospital 2 (Community Clinic - ZERO IPF Cases)
        {"id": 300, "value": "<b>Hospital 2: Community Clinic</b> [Zero IPF Cases — True Rare Scarcity]",
         "style": "rounded=1;fillColor=#FDF2E9;strokeColor=#E67E22;strokeWidth=2;verticalAlign=top;align=left;spacingLeft=15;spacingTop=10;fontColor=#0A2540;fontSize=13;fontStyle=1;",
         "x": 590, "y": 390, "w": 460, "h": 530},

        {"id": 301, "value": "<b>Private HRCT Dataset</b><br><b>0 IPF</b> | 21 COPD | 150 Norm<br>GE LightSpeed Scanner",
         "style": "shape=cylinder3;size=15;fillColor=#F8CECC;strokeColor=#B85450;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 615, "y": 445, "w": 200, "h": 80},

        {"id": 302, "value": "<b>Local Classifier (F_θ_2)</b><br>No Real IPF Training Scans<br>Prone to class collapse",
         "style": "rounded=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 835, "y": 445, "w": 190, "h": 80},

        {"id": 303, "value": "<b>Zero-Patient Distillation Adapter</b><br>Distills G_ψ using global class prototypes<br>No division-by-zero errors",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 615, "y": 550, "w": 410, "h": 70},

        {"id": 304, "value": "<b>Generative Latent Replay Engine</b><br><b>Synthesizes 100% of Rare IPF Latents!</b><br>Restores balanced gradient signal",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=11;fontStyle=1;align=center;",
         "x": 615, "y": 645, "w": 410, "h": 70},

        {"id": 305, "value": "<b>Hospital 2 Federated Client Node</b><br>Receives (θ, ψ) • Computes (Δθ_2, Δψ_2) • Secure Upload",
         "style": "rounded=1;fillColor=#FDF2E9;strokeColor=#E67E22;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 615, "y": 740, "w": 410, "h": 65},

        # Hospital 3 (Rural District Hospital - 1 IPF Case)
        {"id": 400, "value": "<b>Hospital 3: Rural District Hospital</b> [1 IPF Patient — Single Anchor]",
         "style": "rounded=1;fillColor=#F5F7FA;strokeColor=#1A5FB4;strokeWidth=2;verticalAlign=top;align=left;spacingLeft=15;spacingTop=10;fontColor=#0A2540;fontSize=13;fontStyle=1;",
         "x": 1100, "y": 390, "w": 460, "h": 530},

        {"id": 401, "value": "<b>Private HRCT Dataset</b><br><b>1 IPF</b> | 142 COPD | 80 Norm<br>Philips Ingenuity Scanner",
         "style": "shape=cylinder3;size=15;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 1125, "y": 445, "w": 200, "h": 80},

        {"id": 402, "value": "<b>Local Classifier (F_θ_3)</b><br>Single IPF anchor instance<br>IntraSCL cannot form pairs",
         "style": "rounded=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 1345, "y": 445, "w": 190, "h": 80},

        {"id": 403, "value": "<b>FedIIC IntraSCL Failure Point</b><br>|P(i)| = 0 positive pairs → Contrastive Collapse<br>DALA prior log(0) → -∞ penalty",
         "style": "rounded=1;fillColor=#F8CECC;strokeColor=#B85450;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 1125, "y": 550, "w": 410, "h": 70},

        {"id": 404, "value": "<b>Generative Latent Replay Solution</b><br>Supplies synthetic positive pairs for IntraSCL<br>Eliminates negative DALA bias",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=11;fontStyle=1;align=center;",
         "x": 1125, "y": 645, "w": 410, "h": 70},

        {"id": 405, "value": "<b>Hospital 3 Federated Client Node</b><br>Receives (θ, ψ) • Computes (Δθ_3, Δψ_3) • Secure Upload",
         "style": "rounded=1;fillColor=#EBF3FB;strokeColor=#1A5FB4;fontColor=#0A2540;fontSize=11;align=center;",
         "x": 1125, "y": 740, "w": 410, "h": 65},

        # Flow Edges
        {"id": 501, "edge": True, "source": 104, "target": 205, "value": "Broadcast (θ, ψ)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#1A5FB4;strokeWidth=2;exitX=0.25;exitY=1;entryX=0.5;entryY=0;"},
        {"id": 502, "edge": True, "source": 104, "target": 305, "value": "Broadcast (θ, ψ)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#1A5FB4;strokeWidth=2;exitX=0.5;exitY=1;entryX=0.5;entryY=0;"},
        {"id": 503, "edge": True, "source": 104, "target": 405, "value": "Broadcast (θ, ψ)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#1A5FB4;strokeWidth=2;exitX=0.75;exitY=1;entryX=0.5;entryY=0;"},

        {"id": 504, "edge": True, "source": 205, "target": 103, "value": "Upload (Δθ_1, Δψ_1)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#27AE60;strokeWidth=2;dashed=1;exitX=0.75;exitY=1;entryX=0.25;entryY=1;"},
        {"id": 505, "edge": True, "source": 305, "target": 103, "value": "Upload (Δθ_2, Δψ_2)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#27AE60;strokeWidth=2;dashed=1;exitX=0.75;exitY=1;entryX=0.5;entryY=1;"},
        {"id": 506, "edge": True, "source": 405, "target": 103, "value": "Upload (Δθ_3, Δψ_3)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#27AE60;strokeWidth=2;dashed=1;exitX=0.75;exitY=1;entryX=0.75;entryY=1;"}
    ]
    with open(os.path.join(out_dir, "01_component_diagram.drawio"), "wb") as f:
        f.write(create_drawio_xml("Component Diagram", comp_elements, 1700, 1050))

    # ─────────────────────────────────────────────────────────────
    # 2. CLASS DIAGRAM (docs/uml/02_class_diagram.drawio)
    # ─────────────────────────────────────────────────────────────
    class_elements = [
        # Top Row: Config, Dataset, Generator, Metrics
        {"id": 10, "value": "<b>Config</b><br>+ disease_target: str = 'IPF'<br>+ num_classes: int = 3<br>+ rare_class_idx: int = 0<br>+ num_clients: int = 5<br>+ non_iid_alpha: float = 0.2<br>+ global_rounds: int = 12<br>+ feature_dim: int = 128<br>+ noise_dim: int = 64<br>+ to_dict(): dict",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;startSize=28;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=12;",
         "x": 60, "y": 50, "w": 320, "h": 260},

        {"id": 20, "value": "<b>IPFChestCTDataset</b><br>+ images: Tensor[N, 1, 64, 64]<br>+ labels: Tensor[N]<br>+ scanner_ids: Tensor[N]<br>+ class_counts: list[int]<br>+ __len__(): int<br>+ __getitem__(idx: int): tuple[Tensor, int]<br>+ get_class_counts(): list[int]<br>+ get_scanner_distribution(): dict",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;startSize=28;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=12;",
         "x": 440, "y": 50, "w": 360, "h": 260},

        {"id": 30, "value": "<b>ConditionalFeatureGenerator</b><br>- label_embed: nn.Embedding(3, 64)<br>- mlp_layers: nn.Sequential<br>+ forward(noise: Tensor, labels: Tensor): Tensor<br>+ sample(labels: Tensor, device: str): Tensor<br>+ compute_diversity_loss(z1, z2): Tensor",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;startSize=28;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=12;",
         "x": 860, "y": 50, "w": 380, "h": 260},

        {"id": 40, "value": "<b>MetricsEvaluator</b><br>+ compute_all_metrics(y_true, y_pred, y_prob): dict<br>+ balanced_accuracy(y_true, y_pred): float<br>+ rare_class_recall(y_true, y_pred): float<br>+ macro_f1_score(y_true, y_pred): float<br>+ auroc_multiclass(y_true, y_prob): float",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;startSize=28;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#0A2540;fontSize=12;",
         "x": 1300, "y": 50, "w": 340, "h": 260},

        # Middle Row: Abstract Model and Backbones
        {"id": 50, "value": "<b>&laquo;abstract&raquo;<br>BaseClassifier</b><br>+ extract_features(x: Tensor): Tensor[B, 128]<br>+ forward_head(feat: Tensor): Tensor[B, 3]<br>+ forward(x: Tensor, return_proj: bool): tuple",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;startSize=28;fillColor=#FFF2CC;strokeColor=#D6B656;fontColor=#0A2540;fontSize=12;",
         "x": 440, "y": 380, "w": 360, "h": 170},

        {"id": 51, "value": "<b>ConvNet</b><br>- conv_layers: nn.Sequential (4 blocks)<br>- feature_proj: nn.LayerNorm(128)<br>- classifier_head: nn.Linear(128, 3)<br>- projector_head: nn.Sequential (128 -> 64)<br>+ extract_features(x: Tensor): Tensor<br>+ forward_head(feat: Tensor): Tensor",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;startSize=28;fillColor=#FFF2CC;strokeColor=#D6B656;fontColor=#0A2540;fontSize=12;",
         "x": 220, "y": 620, "w": 360, "h": 220},

        {"id": 52, "value": "<b>ResNet18Classifier</b><br>- resnet_backbone: torchvision.models.resnet18<br>- custom_fc: nn.Linear(512, 128)<br>- classifier_head: nn.Linear(128, 3)<br>- projector_head: nn.Sequential(128 -> 64)<br>+ extract_features(x: Tensor): Tensor<br>+ forward_head(feat: Tensor): Tensor",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;startSize=28;fillColor=#FFF2CC;strokeColor=#D6B656;fontColor=#0A2540;fontSize=12;",
         "x": 640, "y": 620, "w": 360, "h": 220},

        # Federated Edge & Server Classes
        {"id": 60, "value": "<b>HospitalClient</b><br>+ client_id: int<br>+ dataset: IPFChestCTDataset<br>+ total_samples: int<br>+ rare_samples: int<br>+ local_classifier: BaseClassifier<br>+ local_generator: ConditionalFeatureGenerator<br>+ train_classifier_standard(): tuple[dict, float]<br>+ train_classifier_fediic(): tuple[dict, float]<br>+ train_classifier_with_replay(): tuple[dict, float]<br>+ train_generator_locally(): tuple[dict, float]<br>+ compute_real_feature_centroids(): dict[int, Tensor]",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;startSize=28;fillColor=#F5F7FA;strokeColor=#1A5FB4;fontColor=#0A2540;fontSize=12;",
         "x": 1080, "y": 380, "w": 480, "h": 330},

        {"id": 70, "value": "<b>FederatedServer</b><br>+ clients: list[HospitalClient]<br>+ test_dataset: IPFChestCTDataset<br>+ global_classifier: BaseClassifier<br>+ global_generator: ConditionalFeatureGenerator<br>+ aggregate_weights(weights_list, sample_weights): dict<br>+ train_round_fedavg(): float<br>+ train_round_fedprox(mu: float): float<br>+ train_round_fediic(): float<br>+ train_round_fedgen_rare(): float<br>+ evaluate_global(classifier): dict[str, float]",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;startSize=28;fillColor=#EBF3FB;strokeColor=#1A5FB4;fontColor=#0A2540;fontSize=12;",
         "x": 1080, "y": 780, "w": 480, "h": 320},

        # Associations & Relationships
        {"id": 81, "edge": True, "source": 51, "target": 50, "value": "inherits",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;endFill=0;strokeColor=#0A2540;strokeWidth=2;"},
        {"id": 82, "edge": True, "source": 52, "target": 50, "value": "inherits",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;endFill=0;strokeColor=#0A2540;strokeWidth=2;"},
        {"id": 83, "edge": True, "source": 60, "target": 20, "value": "holds 1",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=diamond;endFill=1;strokeColor=#0A2540;strokeWidth=2;"},
        {"id": 84, "edge": True, "source": 70, "target": 60, "value": "orchestrates 1..K",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=diamond;endFill=1;strokeColor=#0A2540;strokeWidth=2;"},
        {"id": 85, "edge": True, "source": 70, "target": 50, "value": "maintains global",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;strokeColor=#0A2540;strokeWidth=2;"},
        {"id": 86, "edge": True, "source": 70, "target": 30, "value": "maintains global",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;strokeColor=#0A2540;strokeWidth=2;"},
        {"id": 87, "edge": True, "source": 70, "target": 40, "value": "uses for evaluation",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;dashed=1;strokeColor=#0A2540;strokeWidth=2;"}
    ]
    with open(os.path.join(out_dir, "02_class_diagram.drawio"), "wb") as f:
        f.write(create_drawio_xml("Class Diagram", class_elements, 1750, 1200))

    # ─────────────────────────────────────────────────────────────
    # 3. SEQUENCE DIAGRAM (docs/uml/03_sequence_diagram.drawio)
    # ─────────────────────────────────────────────────────────────
    seq_elements = [
        # Lifeline Headers (Top row, spacious & distinct)
        {"id": 1, "value": "<b>Federated Server Coordinator</b>", "style": "rounded=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=12;fontStyle=1;", "x": 100, "y": 40, "w": 220, "h": 50},
        {"id": 2, "value": "<b>Global Model Store (θ, ψ)</b>", "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=12;fontStyle=1;", "x": 420, "y": 40, "w": 220, "h": 50},
        {"id": 3, "value": "<b>Hospital 1 (Tertiary - High IPF)</b>", "style": "rounded=1;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;fontSize=12;fontStyle=1;", "x": 740, "y": 40, "w": 240, "h": 50},
        {"id": 4, "value": "<b>Hospital 2 (Community - 0 IPF)</b>", "style": "rounded=1;fillColor=#F8CECC;strokeColor=#B85450;fontColor=#0A2540;fontSize=12;fontStyle=1;", "x": 1080, "y": 40, "w": 240, "h": 50},
        {"id": 5, "value": "<b>Global Test Evaluator</b>", "style": "rounded=1;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#0A2540;fontSize=12;fontStyle=1;", "x": 1400, "y": 40, "w": 220, "h": 50},

        # Lifeline vertical rails
        {"id": 11, "value": "", "style": "line;strokeWidth=2;dashed=1;direction=south;strokeColor=#B0B5C0;", "x": 205, "y": 90, "w": 10, "h": 1000},
        {"id": 12, "value": "", "style": "line;strokeWidth=2;dashed=1;direction=south;strokeColor=#B0B5C0;", "x": 525, "y": 90, "w": 10, "h": 1000},
        {"id": 13, "value": "", "style": "line;strokeWidth=2;dashed=1;direction=south;strokeColor=#B0B5C0;", "x": 855, "y": 90, "w": 10, "h": 1000},
        {"id": 14, "value": "", "style": "line;strokeWidth=2;dashed=1;direction=south;strokeColor=#B0B5C0;", "x": 1195, "y": 90, "w": 10, "h": 1000},
        {"id": 15, "value": "", "style": "line;strokeWidth=2;dashed=1;direction=south;strokeColor=#B0B5C0;", "x": 1505, "y": 90, "w": 10, "h": 1000},

        # Phase 1 Banner: STAGE 1 — Federated Generator Distillation
        {"id": 20, "value": "<b>STAGE 1: Federated Generator Distillation (Learning the Latent Space)</b>",
         "style": "shape=note;whiteSpace=wrap;html=1;size=14;verticalAlign=top;align=left;spacingLeft=10;fillColor=#FFF2CC;strokeColor=#D6B656;fontColor=#0A2540;fontSize=12;fontStyle=1;",
         "x": 80, "y": 120, "w": 460, "h": 35},

        {"id": 21, "edge": True, "source": 1, "target": 3, "value": "1. Distribute Global Parameters (θ_glob, ψ_glob)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#1A5FB4;strokeWidth=2;exitY=0.15;entryY=0.15;"},
        {"id": 22, "edge": True, "source": 1, "target": 4, "value": "1. Distribute Global Parameters (θ_glob, ψ_glob)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#1A5FB4;strokeWidth=2;exitY=0.20;entryY=0.20;"},

        {"id": 23, "value": "<b>Local G_ψ Distillation</b><br>Loss = L_CE + λ_fm L_FM - λ_div L_DIV<br>Anchored to real clinic IPF centroids",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=10;align=center;",
         "x": 760, "y": 240, "w": 220, "h": 55},

        {"id": 24, "value": "<b>Zero-Patient Distillation</b><br>Uses broadcast global class prototypes<br>No division-by-zero crashes",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=10;align=center;",
         "x": 1090, "y": 305, "w": 220, "h": 55},

        {"id": 25, "edge": True, "source": 3, "target": 1, "value": "Return local generator delta Δψ_1",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#27AE60;strokeWidth=2;dashed=1;exitY=0.38;entryY=0.38;"},
        {"id": 26, "edge": True, "source": 4, "target": 1, "value": "Return local generator delta Δψ_2",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#27AE60;strokeWidth=2;dashed=1;exitY=0.43;entryY=0.43;"},
        {"id": 27, "edge": True, "source": 1, "target": 2, "value": "Aggregate: ψ_glob = Σ (n_k/N) ψ_k",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#D79B00;strokeWidth=2;exitY=0.48;entryY=0.48;"},

        # Phase 2 Banner: STAGE 2 — Generative Replay Classifier Update
        {"id": 30, "value": "<b>STAGE 2: Generative Replay Classifier Update (Synthesizing Rare Disease Signals)</b>",
         "style": "shape=note;whiteSpace=wrap;html=1;size=14;verticalAlign=top;align=left;spacingLeft=10;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=12;fontStyle=1;",
         "x": 80, "y": 550, "w": 520, "h": 35},

        {"id": 31, "edge": True, "source": 1, "target": 3, "value": "2. Distribute Aggregated ψ_glob",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#1A5FB4;strokeWidth=2;exitY=0.55;entryY=0.55;"},
        {"id": 32, "edge": True, "source": 1, "target": 4, "value": "2. Distribute Aggregated ψ_glob",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#1A5FB4;strokeWidth=2;exitY=0.60;entryY=0.60;"},

        {"id": 33, "value": "<b>Dynamic Latent Replay</b><br>Sample f̂_IPF ~ G_ψ(z, y=IPF)<br>Replenish rare cases in local mini-batch",
         "style": "rounded=1;fillColor=#FFF2CC;strokeColor=#D6B656;fontColor=#0A2540;fontSize=10;align=center;",
         "x": 1090, "y": 680, "w": 230, "h": 55},

        {"id": 34, "value": "<b>Classifier Training on Replay</b><br>L_clf = CrossEntropy(f_comb, y_comb)<br>Balanced diagnostic decision boundary",
         "style": "rounded=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=10;align=center;",
         "x": 1090, "y": 745, "w": 230, "h": 55},

        {"id": 35, "edge": True, "source": 3, "target": 1, "value": "Return local classifier delta Δθ_1",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#27AE60;strokeWidth=2;dashed=1;exitY=0.76;entryY=0.76;"},
        {"id": 36, "edge": True, "source": 4, "target": 1, "value": "Return local classifier delta Δθ_2",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#27AE60;strokeWidth=2;dashed=1;exitY=0.81;entryY=0.81;"},
        {"id": 37, "edge": True, "source": 1, "target": 2, "value": "Aggregate: θ_glob = Σ (n_k/N) θ_k",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#D79B00;strokeWidth=2;exitY=0.86;entryY=0.86;"},

        # Phase 3: Global Multi-Center Evaluation
        {"id": 40, "edge": True, "source": 1, "target": 5, "value": "evaluate_global(θ_glob on held-out multi-center CT)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#9673A6;strokeWidth=2;exitY=0.92;entryY=0.92;"},
        {"id": 41, "edge": True, "source": 5, "target": 1, "value": "Return Clinical Metrics (BACC, Recall, Macro-F1, AUROC)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#9673A6;strokeWidth=2;dashed=1;exitY=0.97;entryY=0.97;"}
    ]
    with open(os.path.join(out_dir, "03_sequence_diagram.drawio"), "wb") as f:
        f.write(create_drawio_xml("Sequence Diagram", seq_elements, 1750, 1200))

    # ─────────────────────────────────────────────────────────────
    # 4. USE CASE DIAGRAM (docs/uml/04_usecase_diagram.drawio)
    # ─────────────────────────────────────────────────────────────
    usecase_elements = [
        # Actors
        {"id": 1, "value": "<b>Hospital Radiologist / Clinician</b>", "style": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;fontColor=#0A2540;fontSize=11;", "x": 70, "y": 180, "w": 45, "h": 90},
        {"id": 2, "value": "<b>Hospital Node Administrator</b>", "style": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;fontColor=#0A2540;fontSize=11;", "x": 70, "y": 500, "w": 45, "h": 90},
        {"id": 3, "value": "<b>Server Coordinator / Researcher</b>", "style": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;fontColor=#0A2540;fontSize=11;", "x": 1540, "y": 340, "w": 45, "h": 90},

        # System Boundary Box
        {"id": 10, "value": "<b>FedGen-Rare Platform System Boundary</b>",
         "style": "rounded=1;fillColor=#FAFAFA;strokeColor=#1A5FB4;strokeWidth=2;verticalAlign=top;align=left;spacingLeft=20;spacingTop=12;fontColor=#0A2540;fontSize=14;fontStyle=1;",
         "x": 220, "y": 40, "w": 1260, "h": 820},

        # Column 1: Hospital Edge Operations (x = 280)
        {"id": 11, "value": "Acquire &amp; Preprocess<br>Local DICOM HRCT Scans",
         "style": "ellipse;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 280, "y": 100, "w": 260, "h": 70},

        {"id": 12, "value": "Monitor Local Class<br>Imbalance &amp; Rarity Deficit",
         "style": "ellipse;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 280, "y": 210, "w": 260, "h": 70},

        {"id": 13, "value": "Synthesize Latent IPF<br>Features via G_ψ Replay",
         "style": "ellipse;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 280, "y": 320, "w": 260, "h": 70},

        {"id": 14, "value": "Train Local Classifier with<br>Generative Feature Replay",
         "style": "ellipse;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 280, "y": 430, "w": 260, "h": 70},

        {"id": 15, "value": "Verify Zero Raw Image Leakage<br>(Privacy Audit &amp; Firewall Check)",
         "style": "ellipse;fillColor=#FFF2CC;strokeColor=#D6B656;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 280, "y": 540, "w": 260, "h": 70},

        {"id": 16, "value": "Distill Latent Generator<br>on Local Representations",
         "style": "ellipse;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 280, "y": 650, "w": 260, "h": 70},

        # Column 2: Federated Consortium Coordination (x = 680)
        {"id": 21, "value": "Register Hospital Node<br>in Federated Consortium",
         "style": "ellipse;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 680, "y": 150, "w": 280, "h": 70},

        {"id": 22, "value": "Distribute Global Model<br>Parameters (θ_glob, ψ_glob)",
         "style": "ellipse;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 680, "y": 290, "w": 280, "h": 70},

        {"id": 23, "value": "Perform Weighted Parameter<br>Aggregation (FedAvg)",
         "style": "ellipse;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 680, "y": 430, "w": 280, "h": 70},

        {"id": 24, "value": "Track Round Convergence &amp;<br>Loss Synchronization",
         "style": "ellipse;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 680, "y": 570, "w": 280, "h": 70},

        # Column 3: Research, Testing & Clinical Evaluation (x = 1080)
        {"id": 31, "value": "Execute 4-Way Comparative<br>Benchmark (FedAvg/Prox/IIC/Gen)",
         "style": "ellipse;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 1080, "y": 150, "w": 280, "h": 70},

        {"id": 32, "value": "Run Automated Unit Tests<br>(pytest 9.1 Test Suite)",
         "style": "ellipse;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 1080, "y": 290, "w": 280, "h": 70},

        {"id": 33, "value": "Compute Clinical Metrics<br>(BACC, Recall, F1, AUROC)",
         "style": "ellipse;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 1080, "y": 430, "w": 280, "h": 70},

        {"id": 34, "value": "Export LaTeX Reports &amp;<br>Statistical Result Tables",
         "style": "ellipse;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#0A2540;fontSize=12;align=center;",
         "x": 1080, "y": 570, "w": 280, "h": 70},

        # Actor Edges (Clean connections without crossing)
        {"id": 101, "edge": True, "source": 1, "target": 11, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 102, "edge": True, "source": 1, "target": 12, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 103, "edge": True, "source": 1, "target": 13, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 104, "edge": True, "source": 1, "target": 14, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},

        {"id": 105, "edge": True, "source": 2, "target": 15, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 106, "edge": True, "source": 2, "target": 16, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 107, "edge": True, "source": 2, "target": 21, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},

        {"id": 108, "edge": True, "source": 3, "target": 22, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 109, "edge": True, "source": 3, "target": 23, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 110, "edge": True, "source": 3, "target": 24, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 111, "edge": True, "source": 3, "target": 31, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 112, "edge": True, "source": 3, "target": 32, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 113, "edge": True, "source": 3, "target": 33, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 114, "edge": True, "source": 3, "target": 34, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"}
    ]
    with open(os.path.join(out_dir, "04_usecase_diagram.drawio"), "wb") as f:
        f.write(create_drawio_xml("Use Case Diagram", usecase_elements, 1750, 950))

    print("[SUCCESS] Regenerated all 4 spacious, valid Draw.io (.drawio) XML diagram files in docs/uml/")

if __name__ == "__main__":
    generate_all_drawio()
