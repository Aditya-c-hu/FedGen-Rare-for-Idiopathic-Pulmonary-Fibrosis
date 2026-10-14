"""
Generate native Draw.io (.drawio) XML diagram files
for seamless drag-and-drop opening in Draw.io / diagrams.net.
"""
import os
import xml.etree.ElementTree as ET

def create_drawio_xml(diagram_name, elements):
    """
    Creates a valid mxGraphModel XML document for Draw.io.
    """
    mxfile = ET.Element("mxfile", host="app.diagrams.net", version="21.0.0")
    diagram = ET.SubElement(mxfile, "diagram", id="diag1", name=diagram_name)
    model = ET.SubElement(
        diagram, "mxGraphModel",
        dx="1400", dy="900", grid="1", gridSize="10",
        guides="1", tooltips="1", connect="1", arrows="1",
        fold="1", page="1", pageScale="1", pageWidth="1400", pageHeight="900",
        math="0", shadow="0"
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    for el in elements:
        cell = ET.SubElement(root, "mxCell", id=str(el["id"]))
        cell.set("parent", str(el.get("parent", 1)))
        
        if el.get("edge"):
            cell.set("edge", "1")
            cell.set("source", str(el["source"]))
            cell.set("target", str(el["target"]))
            cell.set("style", el.get("style", "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#1A5FB4;strokeWidth=2;"))
            if "value" in el:
                cell.set("value", el["value"])
            geo = ET.SubElement(cell, "mxGeometry", relative="1", as_="geometry")
        else:
            cell.set("vertex", "1")
            cell.set("value", el["value"])
            cell.set("style", el.get("style", "rounded=1;whiteSpace=wrap;html=1;"))
            geo = ET.SubElement(
                cell, "mxGeometry",
                x=str(el["x"]), y=str(el["y"]),
                width=str(el["w"]), height=str(el["h"]),
                as_="geometry"
            )

    return ET.tostring(mxfile, encoding="utf-8", xml_declaration=True)

def generate_all_drawio():
    out_dir = "docs/uml"
    os.makedirs(out_dir, exist_ok=True)

    # ─────────────────────────────────────────────────────────────
    # 1. COMPONENT DIAGRAM
    # ─────────────────────────────────────────────────────────────
    comp_elements = [
        # Server Group
        {"id": 100, "value": "<b>Global Federated Server (Trusted Central Aggregator)</b>",
         "style": "swimlane;startSize=26;fillColor=#EBF3FB;strokeColor=#1A5FB4;fontColor=#0A2540;rounded=1;fontStyle=1;align=center;",
         "x": 380, "y": 40, "w": 640, "h": 220},
        {"id": 101, "parent": 100, "value": "<b>Global Classifier</b><br>F_θ (ConvNet / ResNet-18)",
         "style": "rounded=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0A2540;html=1;",
         "x": 30, "y": 40, "w": 180, "h": 65},
        {"id": 102, "parent": 100, "value": "<b>Global Conditional Generator</b><br>G_ψ (Latent Replay)",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#0A2540;html=1;",
         "x": 230, "y": 40, "w": 180, "h": 65},
        {"id": 103, "parent": 100, "value": "<b>FedAvg Aggregator</b><br>θ = Σ (n_k/N) θ_k<br>ψ = Σ (n_k/N) ψ_k",
         "style": "rounded=1;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#0A2540;html=1;",
         "x": 430, "y": 40, "w": 180, "h": 65},
        {"id": 104, "parent": 100, "value": "<b>Federated Server Engine</b><br>(Orchestration & Communication)",
         "style": "rounded=1;fillColor=#F5F7FA;strokeColor=#B0B5C0;fontColor=#0A2540;html=1;",
         "x": 130, "y": 130, "w": 380, "h": 50},

        # Hospital 1 (High IPF)
        {"id": 200, "value": "<b>Hospital 1 (Tertiary Center)</b><br>[High IPF, Siemens CT]",
         "style": "swimlane;startSize=26;fillColor=#F5F7FA;strokeColor=#1A5FB4;fontColor=#0A2540;rounded=1;",
         "x": 60, "y": 380, "w": 360, "h": 260},
        {"id": 201, "parent": 200, "value": "<b>Local HRCT Dataset</b><br>33 IPF | 72 COPD | 296 Norm",
         "style": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#DAE8FC;strokeColor=#6C8EBF;",
         "x": 20, "y": 40, "w": 140, "h": 70},
        {"id": 202, "parent": 200, "value": "<b>Local Classifier</b><br>F_θ_1 (Local Updates)",
         "style": "rounded=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;html=1;",
         "x": 180, "y": 40, "w": 160, "h": 60},
        {"id": 203, "parent": 200, "value": "<b>Local Generator Distillation</b><br>G_ψ_1 (Trained on Local Real Data)",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;html=1;",
         "x": 20, "y": 140, "w": 320, "h": 45},
        {"id": 204, "parent": 200, "value": "<b>Local Generative Replay</b><br>Balances local batches with f̂_IPF",
         "style": "rounded=1;fillColor=#FFF2CC;strokeColor=#D6B656;html=1;",
         "x": 20, "y": 200, "w": 320, "h": 45},

        # Hospital 2 (Zero/Low IPF)
        {"id": 300, "value": "<b>Hospital 2 (Community Clinic)</b><br>[0 IPF Cases, GE CT]",
         "style": "swimlane;startSize=26;fillColor=#FDF2E9;strokeColor=#E67E22;fontColor=#0A2540;rounded=1;",
         "x": 520, "y": 380, "w": 360, "h": 260},
        {"id": 301, "parent": 300, "value": "<b>Local HRCT Dataset</b><br>0 IPF | 21 COPD | 0 Norm",
         "style": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#F8CECC;strokeColor=#B85450;",
         "x": 20, "y": 40, "w": 140, "h": 70},
        {"id": 302, "parent": 300, "value": "<b>Local Classifier</b><br>F_θ_2 (No Real IPF)",
         "style": "rounded=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;html=1;",
         "x": 180, "y": 40, "w": 160, "h": 60},
        {"id": 303, "parent": 300, "value": "<b>Zero-Patient Generator Update</b><br>Distilled from F_θ without local IPF",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;html=1;",
         "x": 20, "y": 140, "w": 320, "h": 45},
        {"id": 304, "parent": 300, "value": "<b>Generative Replay Engine</b><br>Synthesizes 100% of IPF signal!",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;fontStyle=1;html=1;",
         "x": 20, "y": 200, "w": 320, "h": 45},

        # Hospital K (1 IPF Case)
        {"id": 400, "value": "<b>Hospital K (Rural Hospital)</b><br>[1 IPF Case, Philips CT]",
         "style": "swimlane;startSize=26;fillColor=#F5F7FA;strokeColor=#1A5FB4;fontColor=#0A2540;rounded=1;",
         "x": 980, "y": 380, "w": 360, "h": 260},
        {"id": 401, "parent": 400, "value": "<b>Local HRCT Dataset</b><br>1 IPF | 142 COPD | 0 Norm",
         "style": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#FFE6CC;strokeColor=#D79B00;",
         "x": 20, "y": 40, "w": 140, "h": 70},
        {"id": 402, "parent": 400, "value": "<b>Local Classifier</b><br>F_θ_K",
         "style": "rounded=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;html=1;",
         "x": 180, "y": 40, "w": 160, "h": 60},
        {"id": 403, "parent": 400, "value": "<b>Single-Patient Anchor</b><br>FedIIC IntraSCL fails here!",
         "style": "rounded=1;fillColor=#F8CECC;strokeColor=#B85450;html=1;",
         "x": 20, "y": 140, "w": 320, "h": 45},
        {"id": 404, "parent": 400, "value": "<b>Generative Replay Engine</b><br>Synthesizes positive pairs for IPF",
         "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;html=1;",
         "x": 20, "y": 200, "w": 320, "h": 45},

        # Flow Edges
        {"id": 501, "edge": True, "source": 104, "target": 203, "value": "Distribute (θ, ψ)"},
        {"id": 502, "edge": True, "source": 104, "target": 303, "value": "Distribute (θ, ψ)"},
        {"id": 503, "edge": True, "source": 104, "target": 403, "value": "Distribute (θ, ψ)"},
        {"id": 504, "edge": True, "source": 204, "target": 103, "value": "Upload (Δθ_1, Δψ_1)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#27AE60;strokeWidth=2;dashed=1;"},
        {"id": 505, "edge": True, "source": 304, "target": 103, "value": "Upload (Δθ_2, Δψ_2)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#27AE60;strokeWidth=2;dashed=1;"},
        {"id": 506, "edge": True, "source": 404, "target": 103, "value": "Upload (Δθ_K, Δψ_K)",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#27AE60;strokeWidth=2;dashed=1;"}
    ]
    with open(os.path.join(out_dir, "01_component_diagram.drawio"), "wb") as f:
        f.write(create_drawio_xml("Component Diagram", comp_elements))

    # ─────────────────────────────────────────────────────────────
    # 2. CLASS DIAGRAM
    # ─────────────────────────────────────────────────────────────
    class_elements = [
        {"id": 10, "value": "<b>Config</b><br>+ disease_target: str<br>+ num_classes: int = 3<br>+ rare_class_idx: int = 0<br>+ num_clients: int = 5<br>+ non_iid_alpha: float = 0.2<br>+ global_rounds: int = 12<br>+ feature_dim: int = 128<br>+ noise_dim: int = 64<br>+ to_dict(): dict",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;",
         "x": 40, "y": 40, "w": 220, "h": 200},

        {"id": 20, "value": "<b>IPFChestCTDataset</b><br>+ images: Tensor[N,1,64,64]<br>+ labels: Tensor[N]<br>+ scanner_ids: int<br>+ __len__(): int<br>+ __getitem__(idx): tuple<br>+ get_class_counts(): list[int]",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;",
         "x": 300, "y": 40, "w": 230, "h": 160},

        {"id": 30, "value": "<b>&laquo;abstract&raquo;<br>BaseClassifier</b><br>+ extract_features(x): Tensor<br>+ forward_head(feat): Tensor<br>+ forward(x, project): tuple",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;html=1;fillColor=#FFF2CC;strokeColor=#D6B656;",
         "x": 580, "y": 40, "w": 240, "h": 120},

        {"id": 31, "value": "<b>ConvNet</b><br>- encoder: nn.Sequential<br>- feature_proj: LayerNorm<br>- fc: nn.Linear(128, 3)<br>- projector: nn.Sequential<br>+ extract_features(x)<br>+ forward_head(feat)",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;html=1;fillColor=#FFF2CC;strokeColor=#D6B656;",
         "x": 580, "y": 200, "w": 240, "h": 160},

        {"id": 40, "value": "<b>ConditionalFeatureGenerator</b><br>- embedding: nn.Embedding(3, 64)<br>- net: nn.Sequential(MLP)<br>+ forward(noise, labels): Tensor<br>+ sample(labels, device): Tensor",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;html=1;fillColor=#D5E8D4;strokeColor=#82B366;",
         "x": 860, "y": 40, "w": 260, "h": 140},

        {"id": 50, "value": "<b>HospitalClient</b><br>+ client_id: int<br>+ dataset: IPFChestCTDataset<br>+ total_samples: int<br>+ rare_samples: int<br>+ train_classifier_standard(): (dict, float)<br>+ train_classifier_fediic(): (dict, float)<br>+ train_classifier_with_replay(): (dict, float)<br>+ train_generator_locally(): (dict, float)",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;html=1;fillColor=#F5F7FA;strokeColor=#1A5FB4;",
         "x": 180, "y": 280, "w": 350, "h": 200},

        {"id": 60, "value": "<b>FederatedServer</b><br>+ clients: list[HospitalClient]<br>+ test_dataset: IPFChestCTDataset<br>+ global_classifier: BaseClassifier<br>+ global_generator: CondFeatGen<br>+ aggregate_weights(weights_list): dict<br>+ train_round_fedavg(): float<br>+ train_round_fedprox(): float<br>+ train_round_fediic(): float<br>+ train_round_fedgen_rare(): float<br>+ evaluate_global(): dict",
         "style": "swimlane;fontStyle=0;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;html=1;fillColor=#EBF3FB;strokeColor=#1A5FB4;",
         "x": 600, "y": 420, "w": 320, "h": 240},

        # Associations
        {"id": 71, "edge": True, "source": 31, "target": 30, "value": "inherits",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;endFill=0;strokeColor=#0A2540;"},
        {"id": 72, "edge": True, "source": 50, "target": 20, "value": "holds 1",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=diamond;endFill=1;strokeColor=#0A2540;"},
        {"id": 73, "edge": True, "source": 60, "target": 50, "value": "orchestrates 1..K",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=diamond;endFill=1;strokeColor=#0A2540;"},
        {"id": 74, "edge": True, "source": 60, "target": 30, "value": "maintains global",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;strokeColor=#0A2540;"},
        {"id": 75, "edge": True, "source": 60, "target": 40, "value": "maintains global",
         "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;strokeColor=#0A2540;"}
    ]
    with open(os.path.join(out_dir, "02_class_diagram.drawio"), "wb") as f:
        f.write(create_drawio_xml("Class Diagram", class_elements))

    # ─────────────────────────────────────────────────────────────
    # 3. SEQUENCE DIAGRAM
    # ─────────────────────────────────────────────────────────────
    seq_elements = [
        # Lifeline headers
        {"id": 1, "value": "<b>Server Orchestrator</b>", "style": "rounded=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;", "x": 80, "y": 40, "w": 160, "h": 40},
        {"id": 2, "value": "<b>Global Models (θ, ψ)</b>", "style": "rounded=1;fillColor=#D5E8D4;strokeColor=#82B366;", "x": 300, "y": 40, "w": 160, "h": 40},
        {"id": 3, "value": "<b>Hospital 1 (High IPF)</b>", "style": "rounded=1;fillColor=#FFE6CC;strokeColor=#D79B00;", "x": 520, "y": 40, "w": 170, "h": 40},
        {"id": 4, "value": "<b>Hospital 2 (Zero IPF)</b>", "style": "rounded=1;fillColor=#F8CECC;strokeColor=#B85450;", "x": 750, "y": 40, "w": 170, "h": 40},
        {"id": 5, "value": "<b>Evaluation Engine</b>", "style": "rounded=1;fillColor=#E1D5E7;strokeColor=#9673A6;", "x": 980, "y": 40, "w": 150, "h": 40},

        # Lifeline vertical rails
        {"id": 11, "value": "", "style": "line;strokeWidth=1;dashed=1;direction=south;", "x": 155, "y": 80, "w": 10, "h": 600},
        {"id": 12, "value": "", "style": "line;strokeWidth=1;dashed=1;direction=south;", "x": 375, "y": 80, "w": 10, "h": 600},
        {"id": 13, "value": "", "style": "line;strokeWidth=1;dashed=1;direction=south;", "x": 600, "y": 80, "w": 10, "h": 600},
        {"id": 14, "value": "", "style": "line;strokeWidth=1;dashed=1;direction=south;", "x": 830, "y": 80, "w": 10, "h": 600},
        {"id": 15, "value": "", "style": "line;strokeWidth=1;dashed=1;direction=south;", "x": 1050, "y": 80, "w": 10, "h": 600},

        # Stage 1 Box
        {"id": 20, "value": "<b>STAGE 1: Federated Generator Update</b>",
         "style": "shape=note;whiteSpace=wrap;html=1;size=14;verticalAlign=top;align=left;fillColor=#FFF2CC;strokeColor=#D6B656;",
         "x": 60, "y": 120, "w": 280, "h": 35},
        {"id": 21, "edge": True, "source": 1, "target": 3, "value": "1. Distribute (θ, ψ)"},
        {"id": 22, "edge": True, "source": 1, "target": 4, "value": "1. Distribute (θ, ψ)"},
        {"id": 23, "edge": True, "source": 3, "target": 3, "value": "Train G_ψ with Real Centroids"},
        {"id": 24, "edge": True, "source": 4, "target": 4, "value": "Train G_ψ via Distillation"},
        {"id": 25, "edge": True, "source": 3, "target": 1, "value": "Return local generator Δψ_1"},
        {"id": 26, "edge": True, "source": 4, "target": 1, "value": "Return local generator Δψ_2"},
        {"id": 27, "edge": True, "source": 1, "target": 2, "value": "Aggregate: ψ_glob = Σ (n_k/N) ψ_k"},

        # Stage 2 Box
        {"id": 30, "value": "<b>STAGE 2: Generative Replay Classifier Update</b>",
         "style": "shape=note;whiteSpace=wrap;html=1;size=14;verticalAlign=top;align=left;fillColor=#D5E8D4;strokeColor=#82B366;",
         "x": 60, "y": 320, "w": 320, "h": 35},
        {"id": 31, "edge": True, "source": 1, "target": 3, "value": "2. Distribute updated ψ_glob"},
        {"id": 32, "edge": True, "source": 1, "target": 4, "value": "2. Distribute updated ψ_glob"},
        {"id": 33, "edge": True, "source": 4, "target": 4, "value": "Sample f̂_IPF from G_ψ to balance batch"},
        {"id": 34, "edge": True, "source": 4, "target": 4, "value": "Train F_θ on [f_real ‖ f̂_IPF]"},
        {"id": 35, "edge": True, "source": 3, "target": 1, "value": "Return local classifier Δθ_1"},
        {"id": 36, "edge": True, "source": 4, "target": 1, "value": "Return local classifier Δθ_2"},
        {"id": 37, "edge": True, "source": 1, "target": 2, "value": "Aggregate: θ_glob = Σ (n_k/N) θ_k"},

        # Evaluation
        {"id": 40, "edge": True, "source": 1, "target": 5, "value": "evaluate_global(F_θ_glob)"},
        {"id": 41, "edge": True, "source": 5, "target": 1, "value": "Return (BACC, Recall, F1, AUROC)"}
    ]
    with open(os.path.join(out_dir, "03_sequence_diagram.drawio"), "wb") as f:
        f.write(create_drawio_xml("Sequence Diagram", seq_elements))

    # ─────────────────────────────────────────────────────────────
    # 4. USE CASE DIAGRAM
    # ─────────────────────────────────────────────────────────────
    usecase_elements = [
        {"id": 1, "value": "Hospital Radiologist", "style": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;", "x": 60, "y": 140, "w": 40, "h": 80},
        {"id": 2, "value": "Federated Server (Aggregator)", "style": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;", "x": 60, "y": 380, "w": 40, "h": 80},
        {"id": 3, "value": "Research Engineer / Developer", "style": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;", "x": 1080, "y": 240, "w": 40, "h": 80},

        # System Boundary
        {"id": 10, "value": "<b>FedGen-Rare Platform</b>", "style": "swimlane;startSize=26;fillColor=#FAFAFA;strokeColor=#1A5FB4;rounded=1;", "x": 180, "y": 40, "w": 820, "h": 540},
        {"id": 11, "parent": 10, "value": "Load Local Private HRCT Scans", "style": "ellipse;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;", "x": 60, "y": 40, "w": 220, "h": 60},
        {"id": 12, "parent": 10, "value": "Train Local Classifier with Replay", "style": "ellipse;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;", "x": 60, "y": 120, "w": 220, "h": 60},
        {"id": 13, "parent": 10, "value": "Distill Latent Generator Locally", "style": "ellipse;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#82B366;", "x": 60, "y": 200, "w": 220, "h": 60},
        {"id": 14, "parent": 10, "value": "Coordinate Global Communication Rounds", "style": "ellipse;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#D79B00;", "x": 60, "y": 300, "w": 240, "h": 60},
        {"id": 15, "parent": 10, "value": "Aggregate Model Parameters (FedAvg)", "style": "ellipse;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#D79B00;", "x": 60, "y": 380, "w": 240, "h": 60},
        {"id": 16, "parent": 10, "value": "Execute 4-Way Comparative Benchmark", "style": "ellipse;whiteSpace=wrap;html=1;fillColor=#E1D5E7;strokeColor=#9673A6;", "x": 480, "y": 120, "w": 260, "h": 60},
        {"id": 17, "parent": 10, "value": "Run Automated Unit Tests (pytest)", "style": "ellipse;whiteSpace=wrap;html=1;fillColor=#E1D5E7;strokeColor=#9673A6;", "x": 480, "y": 220, "w": 260, "h": 60},
        {"id": 18, "parent": 10, "value": "Generate Diagnostic Metrics & Visuals", "style": "ellipse;whiteSpace=wrap;html=1;fillColor=#E1D5E7;strokeColor=#9673A6;", "x": 480, "y": 320, "w": 260, "h": 60},

        # Actor associations
        {"id": 21, "edge": True, "source": 1, "target": 11, "value": ""},
        {"id": 22, "edge": True, "source": 1, "target": 12, "value": ""},
        {"id": 23, "edge": True, "source": 2, "target": 14, "value": ""},
        {"id": 24, "edge": True, "source": 2, "target": 15, "value": ""},
        {"id": 25, "edge": True, "source": 3, "target": 16, "value": ""},
        {"id": 26, "edge": True, "source": 3, "target": 17, "value": ""},
        {"id": 27, "edge": True, "source": 3, "target": 18, "value": ""}
    ]
    with open(os.path.join(out_dir, "04_usecase_diagram.drawio"), "wb") as f:
        f.write(create_drawio_xml("Use Case Diagram", usecase_elements))

    print("[SUCCESS] Created all 4 native Draw.io (.drawio) XML diagram files in docs/uml/")

if __name__ == "__main__":
    generate_all_drawio()
