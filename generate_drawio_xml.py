"""
Generate native Draw.io (.drawio) XML diagram files
for seamless drag-and-drop opening in Draw.io / diagrams.net.
Fixes geometry parsing (as="geometry"), text wrapping (html=1),
strictly prevents ID 0/1 collisions, and provides spacious,
beautifully aligned component layouts.
"""
import os
import xml.etree.ElementTree as ET

def create_drawio_xml(diagram_name, elements, width=1800, height=1200):
    """
    Creates a strictly valid, spacious mxGraphModel XML document for Draw.io.
    Every mxGeometry MUST have as="geometry".
    Every vertex MUST have html=1 and whiteSpace=wrap.
    Guarantees no element uses reserved IDs '0' or '1'.
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
        cell_id = str(el["id"])
        if cell_id in ["0", "1"]:
            raise ValueError(f"Diagram '{diagram_name}' element cannot use reserved ID '{cell_id}'!")

        cell = ET.SubElement(root, "mxCell", id=cell_id)
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
            if "points" in el:
                arr = ET.SubElement(geo, "Array")
                arr.set("as", "points")
                for px, py in el["points"]:
                    ET.SubElement(arr, "mxPoint", x=str(px), y=str(py))
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
    def build_uml_class(class_name, header_bg, border_color, attributes, methods, is_abstract=False):
        header = f'<div style="background-color:{header_bg};padding:6px 4px;text-align:center;font-weight:bold;border-bottom:1.5px solid {border_color};font-size:12px;color:#0A2540;">'
        if is_abstract:
            header += '<span style="font-size:10px;font-style:italic;font-weight:normal;">&laquo;abstract&raquo;</span><br/>'
        header += f'{class_name}</div>'

        attrs = ''
        if attributes:
            attrs = '<div style="padding:6px 8px;font-size:11px;color:#0A2540;line-height:1.35;text-align:left;">' + '<br/>'.join(attributes) + '</div>'

        meths = ''
        if methods:
            meths = f'<div style="border-top:1px solid #CBD5E1;padding:6px 8px;font-size:11px;color:#0A2540;line-height:1.35;text-align:left;">' + '<br/>'.join(methods) + '</div>'

        return header + attrs + meths

    def cls_style(border_color):
        return f"rounded=1;arcSize=4;fillColor=#FFFFFF;strokeColor={border_color};strokeWidth=1.5;html=1;whiteSpace=wrap;overflow=hidden;align=left;verticalAlign=top;spacing=0;"

    class_elements = [
        # Top Row: Config, Dataset, Generator, Metrics (Compact, well-spaced)
        {"id": 10,
         "value": build_uml_class(
             "Config", "#DAE8FC", "#6C8EBF",
             ["+ disease_target: str = 'IPF'",
              "+ num_classes: int = 3",
              "+ rare_class_idx: int = 0",
              "+ num_clients: int = 5",
              "+ non_iid_alpha: float = 0.2",
              "+ global_rounds: int = 12",
              "+ feature_dim: int = 128",
              "+ noise_dim: int = 64"],
             ["+ to_dict(): dict"]
         ),
         "style": cls_style("#6C8EBF"),
         "x": 50, "y": 50, "w": 220, "h": 195},

        {"id": 20,
         "value": build_uml_class(
             "IPFChestCTDataset", "#DAE8FC", "#6C8EBF",
             ["+ images: Tensor[N, 1, 64, 64]",
              "+ labels: Tensor[N]",
              "+ scanner_ids: Tensor[N]",
              "+ class_counts: list[int]"],
             ["+ __len__(): int",
              "+ __getitem__(idx: int): tuple",
              "+ get_class_counts(): list[int]"]
         ),
         "style": cls_style("#6C8EBF"),
         "x": 310, "y": 50, "w": 260, "h": 165},

        {"id": 30,
         "value": build_uml_class(
             "ConditionalFeatureGenerator", "#D5E8D4", "#82B366",
             ["- label_embed: nn.Embedding(3, 64)",
              "- mlp_layers: nn.Sequential"],
             ["+ forward(noise, labels): Tensor",
              "+ sample(labels, device): Tensor",
              "+ compute_diversity_loss(): Tensor"]
         ),
         "style": cls_style("#82B366"),
         "x": 610, "y": 50, "w": 270, "h": 135},

        {"id": 40,
         "value": build_uml_class(
             "MetricsEvaluator", "#E1D5E7", "#9673A6",
             ["+ metric_names: list[str]"],
             ["+ compute_all_metrics(): dict",
              "+ balanced_accuracy(): float",
              "+ rare_class_recall(): float",
              "+ auroc_multiclass(): float"]
         ),
         "style": cls_style("#9673A6"),
         "x": 920, "y": 50, "w": 240, "h": 135},

        # Middle Row: Abstract Model and Backbones
        {"id": 50,
         "value": build_uml_class(
             "BaseClassifier", "#FFF2CC", "#D6B656",
             [],
             ["+ extract_features(x): Tensor",
              "+ forward_head(feat): Tensor",
              "+ forward(x, project): tuple"],
             is_abstract=True
         ),
         "style": cls_style("#D6B656"),
         "x": 310, "y": 255, "w": 260, "h": 105},

        {"id": 51,
         "value": build_uml_class(
             "ConvNet", "#FFF2CC", "#D6B656",
             ["- conv_layers: nn.Sequential",
              "- feature_proj: nn.LayerNorm",
              "- fc: nn.Linear(128, 3)",
              "- projector: nn.Sequential"],
             ["+ extract_features(x): Tensor",
              "+ forward_head(feat): Tensor"]
         ),
         "style": cls_style("#D6B656"),
         "x": 150, "y": 400, "w": 240, "h": 150},

        {"id": 52,
         "value": build_uml_class(
             "ResNet18Classifier", "#FFF2CC", "#D6B656",
             ["- backbone: resnet18",
              "- custom_fc: nn.Linear(512, 128)",
              "- fc: nn.Linear(128, 3)",
              "- projector: nn.Sequential"],
             ["+ extract_features(x): Tensor",
              "+ forward_head(feat): Tensor"]
         ),
         "style": cls_style("#D6B656"),
         "x": 430, "y": 400, "w": 250, "h": 150},

        # Right Side: Federated Edge & Server Classes
        {"id": 60,
         "value": build_uml_class(
             "HospitalClient", "#F5F7FA", "#1A5FB4",
             ["+ client_id: int",
              "+ dataset: IPFChestCTDataset",
              "+ total_samples: int",
              "+ rare_samples: int",
              "+ local_classifier: BaseClassifier",
              "+ local_generator: CondFeatGen"],
             ["+ train_classifier_standard(): tuple",
              "+ train_classifier_fediic(): tuple",
              "+ train_classifier_with_replay(): tuple",
              "+ train_generator_locally(): tuple",
              "+ compute_real_centroids(): dict"]
         ),
         "style": cls_style("#1A5FB4"),
         "x": 750, "y": 220, "w": 330, "h": 230},

        {"id": 70,
         "value": build_uml_class(
             "FederatedServer", "#EBF3FB", "#1A5FB4",
             ["+ clients: list[HospitalClient]",
              "+ test_dataset: IPFChestCTDataset",
              "+ global_classifier: BaseClassifier",
              "+ global_generator: CondFeatGen"],
             ["+ aggregate_weights(weights): dict",
              "+ train_round_fedavg(): float",
              "+ train_round_fedprox(mu): float",
              "+ train_round_fediic(): float",
              "+ train_round_fedgen_rare(): float",
              "+ evaluate_global(classifier): dict"]
         ),
         "style": cls_style("#1A5FB4"),
         "x": 750, "y": 485, "w": 330, "h": 225},

        # Associations & Relationships
        {"id": 81, "edge": True, "source": 51, "target": 50, "value": "inherits",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;endFill=0;strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 82, "edge": True, "source": 52, "target": 50, "value": "inherits",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;endFill=0;strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 83, "edge": True, "source": 60, "target": 20, "value": "holds 1",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=diamond;endFill=1;strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 84, "edge": True, "source": 70, "target": 60, "value": "orchestrates 1..K",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=diamond;endFill=1;strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 85, "edge": True, "source": 70, "target": 50, "value": "maintains global",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 86, "edge": True, "source": 70, "target": 30, "value": "maintains global",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 87, "edge": True, "source": 70, "target": 40, "value": "evaluates with",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;dashed=1;strokeColor=#0A2540;strokeWidth=1.5;"}
    ]
    with open(os.path.join(out_dir, "02_class_diagram.drawio"), "wb") as f:
        f.write(create_drawio_xml("Class Diagram", class_elements, 1400, 850))

    # ─────────────────────────────────────────────────────────────
    # 3. SEQUENCE DIAGRAM (docs/uml/03_sequence_diagram.drawio)
    # ─────────────────────────────────────────────────────────────
    def ll_style(fill_color, stroke_color):
        return f"shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=0;collapsible=0;recursiveResize=0;outlineConnect=0;size=50;fillColor={fill_color};strokeColor={stroke_color};fontColor=#0A2540;fontStyle=1;fontSize=12;"

    seq_elements = [
        # Native UML Lifelines (IDs 10, 20, 30, 40, 50 - strictly no 0 or 1!)
        {"id": 10, "value": "<b>Federated Server Coordinator</b>",
         "style": ll_style("#DAE8FC", "#6C8EBF"), "x": 80, "y": 50, "w": 220, "h": 980},

        {"id": 20, "value": "<b>Global Model Store (θ, ψ)</b>",
         "style": ll_style("#D5E8D4", "#82B366"), "x": 380, "y": 50, "w": 220, "h": 980},

        {"id": 30, "value": "<b>Hospital 1 (High IPF Center)</b>",
         "style": ll_style("#FFE6CC", "#D79B00"), "x": 680, "y": 50, "w": 220, "h": 980},

        {"id": 40, "value": "<b>Hospital 2 (0 IPF Cases)</b>",
         "style": ll_style("#F8CECC", "#B85450"), "x": 980, "y": 50, "w": 220, "h": 980},

        {"id": 50, "value": "<b>Global Test Evaluator</b>",
         "style": ll_style("#E1D5E7", "#9673A6"), "x": 1280, "y": 50, "w": 220, "h": 980},

        # Stage 1 Banner
        {"id": 100, "value": "<b>STAGE 1: Federated Generator Distillation (Latent Representation Learning)</b>",
         "style": "rounded=1;fillColor=#FFF8E1;strokeColor=#F59E0B;strokeWidth=1.5;fontColor=#B45309;fontSize=12;fontStyle=1;align=left;spacingLeft=15;html=1;whiteSpace=wrap;",
         "x": 80, "y": 125, "w": 1420, "h": 36},

        # Stage 1 Messages
        {"id": 111, "edge": True, "source": 10, "target": 30, "value": "1. Broadcast Global Parameters (θ_glob, ψ_glob)",
         "style": "html=1;verticalAlign=bottom;endArrow=block;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#1A5FB4;strokeWidth=2;",
         "points": [(190, 180), (790, 180)]},

        {"id": 112, "edge": True, "source": 10, "target": 40, "value": "1. Broadcast Global Parameters (θ_glob, ψ_glob)",
         "style": "html=1;verticalAlign=bottom;endArrow=block;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#1A5FB4;strokeWidth=2;",
         "points": [(190, 225), (1090, 225)]},

        {"id": 113, "edge": True, "source": 30, "target": 30, "value": "Train G_ψ locally (Anchored to real IPF centroids via L_FM)",
         "style": "html=1;verticalAlign=bottom;endArrow=block;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#059669;strokeWidth=2;",
         "points": [(790, 270), (850, 270), (850, 310), (790, 310)]},

        {"id": 114, "edge": True, "source": 40, "target": 40, "value": "Zero-Patient Distillation (Guided by global class prototypes)",
         "style": "html=1;verticalAlign=bottom;endArrow=block;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#059669;strokeWidth=2;",
         "points": [(1090, 330), (1150, 330), (1150, 370), (1090, 370)]},

        {"id": 115, "edge": True, "source": 30, "target": 10, "value": "Upload local generator delta Δψ_1",
         "style": "html=1;verticalAlign=bottom;endArrow=open;dashed=1;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#059669;strokeWidth=2;",
         "points": [(790, 395), (190, 395)]},

        {"id": 116, "edge": True, "source": 40, "target": 10, "value": "Upload local generator delta Δψ_2",
         "style": "html=1;verticalAlign=bottom;endArrow=open;dashed=1;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#059669;strokeWidth=2;",
         "points": [(1090, 440), (190, 440)]},

        {"id": 117, "edge": True, "source": 10, "target": 20, "value": "Aggregate: ψ_glob = Σ (n_k/N) ψ_k",
         "style": "html=1;verticalAlign=bottom;endArrow=block;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#D97706;strokeWidth=2;",
         "points": [(190, 485), (490, 485)]},

        # Stage 2 Banner
        {"id": 200, "value": "<b>STAGE 2: Generative Replay Classifier Update (Synthesizing Rare Disease Signals)</b>",
         "style": "rounded=1;fillColor=#ECFDF5;strokeColor=#10B981;strokeWidth=1.5;fontColor=#047857;fontSize=12;fontStyle=1;align=left;spacingLeft=15;html=1;whiteSpace=wrap;",
         "x": 80, "y": 525, "w": 1420, "h": 36},

        # Stage 2 Messages
        {"id": 211, "edge": True, "source": 10, "target": 30, "value": "2. Broadcast Synchronized Generator ψ_glob",
         "style": "html=1;verticalAlign=bottom;endArrow=block;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#1A5FB4;strokeWidth=2;",
         "points": [(190, 580), (790, 580)]},

        {"id": 212, "edge": True, "source": 10, "target": 40, "value": "2. Broadcast Synchronized Generator ψ_glob",
         "style": "html=1;verticalAlign=bottom;endArrow=block;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#1A5FB4;strokeWidth=2;",
         "points": [(190, 625), (1090, 625)]},

        {"id": 213, "edge": True, "source": 40, "target": 40, "value": "Dynamic Latent Replay: Sample f̂_IPF ~ G_ψ to replenish rare cases",
         "style": "html=1;verticalAlign=bottom;endArrow=block;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#D97706;strokeWidth=2;",
         "points": [(1090, 670), (1150, 670), (1150, 710), (1090, 710)]},

        {"id": 214, "edge": True, "source": 40, "target": 40, "value": "Train local classifier F_θ on [f_real ‖ f̂_IPF]",
         "style": "html=1;verticalAlign=bottom;endArrow=block;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#1A5FB4;strokeWidth=2;",
         "points": [(1090, 730), (1150, 730), (1150, 770), (1090, 770)]},

        {"id": 215, "edge": True, "source": 30, "target": 10, "value": "Upload local classifier delta Δθ_1",
         "style": "html=1;verticalAlign=bottom;endArrow=open;dashed=1;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#059669;strokeWidth=2;",
         "points": [(790, 790), (190, 790)]},

        {"id": 216, "edge": True, "source": 40, "target": 10, "value": "Upload local classifier delta Δθ_2",
         "style": "html=1;verticalAlign=bottom;endArrow=open;dashed=1;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#059669;strokeWidth=2;",
         "points": [(1090, 830), (190, 830)]},

        {"id": 217, "edge": True, "source": 10, "target": 20, "value": "Aggregate: θ_glob = Σ (n_k/N) θ_k",
         "style": "html=1;verticalAlign=bottom;endArrow=block;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#D97706;strokeWidth=2;",
         "points": [(190, 855), (490, 855)]},

        # Global Evaluation Banner
        {"id": 300, "value": "<b>GLOBAL EVALUATION: Multi-Center Generalization Benchmarking</b>",
         "style": "rounded=1;fillColor=#FAF5FF;strokeColor=#A855F7;strokeWidth=1.5;fontColor=#7E22CE;fontSize=12;fontStyle=1;align=left;spacingLeft=15;html=1;whiteSpace=wrap;",
         "x": 80, "y": 880, "w": 1420, "h": 36},

        # Evaluation Messages
        {"id": 311, "edge": True, "source": 10, "target": 50, "value": "evaluate_global(F_θ_glob on held-out multi-center CT test set)",
         "style": "html=1;verticalAlign=bottom;endArrow=block;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#7E22CE;strokeWidth=2;",
         "points": [(190, 935), (1390, 935)]},

        {"id": 312, "edge": True, "source": 50, "target": 10, "value": "Return Clinical Metrics (BACC, Recall, Macro-F1, AUROC)",
         "style": "html=1;verticalAlign=bottom;endArrow=open;dashed=1;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;strokeColor=#7E22CE;strokeWidth=2;",
         "points": [(1390, 985), (190, 985)]}
    ]
    with open(os.path.join(out_dir, "03_sequence_diagram.drawio"), "wb") as f:
        f.write(create_drawio_xml("Sequence Diagram", seq_elements, 1600, 1100))

    # ─────────────────────────────────────────────────────────────
    # 4. USE CASE DIAGRAM (docs/uml/04_usecase_diagram.drawio)
    # ─────────────────────────────────────────────────────────────
    usecase_elements = [
        # Actors (IDs 501, 502, 503 - strictly no 0 or 1!)
        {"id": 501, "value": "<b>Hospital Radiologist / Clinician</b>",
         "style": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;fontColor=#0A2540;fontSize=11;html=1;",
         "x": 70, "y": 180, "w": 45, "h": 90},

        {"id": 502, "value": "<b>Hospital Node Administrator</b>",
         "style": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;fontColor=#0A2540;fontSize=11;html=1;",
         "x": 70, "y": 500, "w": 45, "h": 90},

        {"id": 503, "value": "<b>Server Coordinator / Researcher</b>",
         "style": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;fontColor=#0A2540;fontSize=11;html=1;",
         "x": 1540, "y": 340, "w": 45, "h": 90},

        # System Boundary Box
        {"id": 510, "value": "<b>FedGen-Rare Platform System Boundary</b>",
         "style": "rounded=1;fillColor=#FAFAFA;strokeColor=#1A5FB4;strokeWidth=2;verticalAlign=top;align=left;spacingLeft=20;spacingTop=12;fontColor=#0A2540;fontSize=14;fontStyle=1;html=1;whiteSpace=wrap;",
         "x": 220, "y": 40, "w": 1260, "h": 820},

        # Column 1: Hospital Edge Operations (x = 280)
        {"id": 611, "value": "Acquire &amp; Preprocess<br>Local DICOM HRCT Scans",
         "style": "ellipse;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 280, "y": 100, "w": 260, "h": 70},

        {"id": 612, "value": "Monitor Local Class<br>Imbalance &amp; Rarity Deficit",
         "style": "ellipse;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 280, "y": 210, "w": 260, "h": 70},

        {"id": 613, "value": "Synthesize Latent IPF<br>Features via G_ψ Replay",
         "style": "ellipse;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 280, "y": 320, "w": 260, "h": 70},

        {"id": 614, "value": "Train Local Classifier with<br>Generative Feature Replay",
         "style": "ellipse;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 280, "y": 430, "w": 260, "h": 70},

        {"id": 615, "value": "Verify Zero Raw Image Leakage<br>(Privacy Audit &amp; Firewall Check)",
         "style": "ellipse;fillColor=#FFF2CC;strokeColor=#D6B656;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 280, "y": 540, "w": 260, "h": 70},

        {"id": 616, "value": "Distill Latent Generator<br>on Local Representations",
         "style": "ellipse;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 280, "y": 650, "w": 260, "h": 70},

        # Column 2: Federated Consortium Coordination (x = 680)
        {"id": 621, "value": "Register Hospital Node<br>in Federated Consortium",
         "style": "ellipse;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 680, "y": 150, "w": 280, "h": 70},

        {"id": 622, "value": "Distribute Global Model<br>Parameters (θ_glob, ψ_glob)",
         "style": "ellipse;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 680, "y": 290, "w": 280, "h": 70},

        {"id": 623, "value": "Perform Weighted Parameter<br>Aggregation (FedAvg)",
         "style": "ellipse;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 680, "y": 430, "w": 280, "h": 70},

        {"id": 624, "value": "Track Round Convergence &amp;<br>Loss Synchronization",
         "style": "ellipse;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 680, "y": 570, "w": 280, "h": 70},

        # Column 3: Research, Testing & Clinical Evaluation (x = 1080)
        {"id": 631, "value": "Execute 4-Way Comparative<br>Benchmark (FedAvg/Prox/IIC/Gen)",
         "style": "ellipse;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 1080, "y": 150, "w": 280, "h": 70},

        {"id": 632, "value": "Run Automated Unit Tests<br>(pytest 9.1 Test Suite)",
         "style": "ellipse;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 1080, "y": 290, "w": 280, "h": 70},

        {"id": 633, "value": "Compute Clinical Metrics<br>(BACC, Recall, F1, AUROC)",
         "style": "ellipse;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 1080, "y": 430, "w": 280, "h": 70},

        {"id": 634, "value": "Export LaTeX Reports &amp;<br>Statistical Result Tables",
         "style": "ellipse;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#0A2540;fontSize=12;align=center;html=1;whiteSpace=wrap;",
         "x": 1080, "y": 570, "w": 280, "h": 70},

        # Actor Edges
        {"id": 701, "edge": True, "source": 501, "target": 611, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 702, "edge": True, "source": 501, "target": 612, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 703, "edge": True, "source": 501, "target": 613, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 704, "edge": True, "source": 501, "target": 614, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},

        {"id": 705, "edge": True, "source": 502, "target": 615, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 706, "edge": True, "source": 502, "target": 616, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 707, "edge": True, "source": 502, "target": 621, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},

        {"id": 708, "edge": True, "source": 503, "target": 622, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 709, "edge": True, "source": 503, "target": 623, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 710, "edge": True, "source": 503, "target": 624, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 711, "edge": True, "source": 503, "target": 631, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 712, "edge": True, "source": 503, "target": 632, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 713, "edge": True, "source": 503, "target": 633, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"},
        {"id": 714, "edge": True, "source": 503, "target": 634, "value": "", "style": "strokeColor=#0A2540;strokeWidth=1.5;"}
    ]
    with open(os.path.join(out_dir, "04_usecase_diagram.drawio"), "wb") as f:
        f.write(create_drawio_xml("Use Case Diagram", usecase_elements, 1750, 950))

    print("[SUCCESS] Regenerated all 4 spacious, valid Draw.io (.drawio) XML diagram files in docs/uml/")

if __name__ == "__main__":
    generate_all_drawio()
