"""
Renders a publication-quality System Architecture diagram for FedGen-Rare as a high-res PNG image.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def render_system_architecture(output_path="docs/uml/system_architecture_diagram.png"):
    fig, ax = plt.subplots(figsize=(13, 7.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color Palette
    c_server_bg = "#EBF3FB"
    c_server_border = "#1A5FB4"
    c_client_bg = "#F8FAFC"
    c_h1_border = "#2980B9"
    c_h2_border = "#E67E22"
    c_hk_border = "#8E44AD"
    c_box_clf = "#DAE8FC"
    c_box_gen = "#D5E8D4"
    c_box_agg = "#FFE6CC"
    c_down_arrow = "#1A5FB4"
    c_up_arrow = "#27AE60"
    c_text_dark = "#0A2540"

    # 1. Global Federated Server Box (Top)
    server_rect = patches.FancyBboxPatch(
        (10, 64), 80, 31, boxstyle="round,pad=0.8,rounding_size=2",
        facecolor=c_server_bg, edgecolor=c_server_border, linewidth=2.5
    )
    ax.add_patch(server_rect)
    ax.text(50, 91.5, "GLOBAL FEDERATED SERVER (TRUSTED AGGREGATOR)",
            ha="center", va="center", fontsize=12.5, fontweight="bold", color=c_server_border)

    # Server inner components
    # Box 1: Global Classifier
    clf_rect = patches.FancyBboxPatch((13, 67), 21, 20, boxstyle="round,pad=0.5,rounding_size=1.5",
                                      facecolor=c_box_clf, edgecolor="#6C8EBF", linewidth=1.5)
    ax.add_patch(clf_rect)
    ax.text(23.5, 83.5, "Global Classifier", ha="center", va="center", fontsize=10.5, fontweight="bold", color=c_text_dark)
    ax.text(23.5, 78.5, r"$\mathcal{F}_\theta$ (ConvNet / ResNet)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1A5FB4")
    ax.text(23.5, 72.5, "128-dim Latent Head\n3 Classes: IPF, COPD, Norm", ha="center", va="center", fontsize=8, color="#333333")

    # Box 2: Global Generator
    gen_rect = patches.FancyBboxPatch((38, 67), 24, 20, boxstyle="round,pad=0.5,rounding_size=1.5",
                                      facecolor=c_box_gen, edgecolor="#82B366", linewidth=1.5)
    ax.add_patch(gen_rect)
    ax.text(50, 83.5, "Global Feature Generator", ha="center", va="center", fontsize=10.5, fontweight="bold", color=c_text_dark)
    ax.text(50, 78.5, r"$\mathcal{G}_\psi(z, y)$ (Conditional MLP)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#27AE60")
    ax.text(50, 72.5, "Synthesizes Rare IPF\nLatent Features: " + r"$\hat{f} \sim p(f|y)$", ha="center", va="center", fontsize=8, color="#333333")

    # Box 3: Model Aggregator
    agg_rect = patches.FancyBboxPatch((66, 67), 21, 20, boxstyle="round,pad=0.5,rounding_size=1.5",
                                      facecolor=c_box_agg, edgecolor="#D79B00", linewidth=1.5)
    ax.add_patch(agg_rect)
    ax.text(76.5, 83.5, "FedAvg Aggregator", ha="center", va="center", fontsize=10.5, fontweight="bold", color=c_text_dark)
    ax.text(76.5, 78.0, r"$\theta_{t+1} = \sum \frac{n_k}{N} \theta_k$", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#D35400")
    ax.text(76.5, 72.5, r"$\psi_{t+1} = \sum \frac{n_k}{N} \psi_k$" + "\nSynchronous Rounds", ha="center", va="center", fontsize=8.5, color="#333333")

    # Privacy Banner
    priv_rect = patches.FancyBboxPatch((24, 58.5), 52, 4.2, boxstyle="round,pad=0.3,rounding_size=1",
                                       facecolor="#D4EDDA", edgecolor="#28A745", linewidth=1.2)
    ax.add_patch(priv_rect)
    ax.text(50, 60.6, "PRIVACY GUARANTEE: Zero Raw Patient CT Scans Exchanged (HIPAA & GDPR Compliant)",
            ha="center", va="center", fontsize=8.5, fontweight="bold", color="#155724")

    # Arrows Downward: Distribution
    ax.annotate("", xy=(22, 48), xytext=(22, 57.5),
                arrowprops=dict(arrowstyle="->", color=c_down_arrow, lw=2.2))
    ax.text(20, 52.5, r"Distribute $(\theta, \psi)$", ha="right", va="center", fontsize=8.5, fontweight="bold", color=c_down_arrow)

    ax.annotate("", xy=(50, 48), xytext=(50, 57.5),
                arrowprops=dict(arrowstyle="->", color=c_down_arrow, lw=2.2))
    ax.text(50, 52.5, r"Broadcast $(\theta, \psi)$", ha="center", va="center", fontsize=8.5, fontweight="bold", color=c_down_arrow)

    ax.annotate("", xy=(78, 48), xytext=(78, 57.5),
                arrowprops=dict(arrowstyle="->", color=c_down_arrow, lw=2.2))
    ax.text(80, 52.5, r"Distribute $(\theta, \psi)$", ha="left", va="center", fontsize=8.5, fontweight="bold", color=c_down_arrow)

    # Arrows Upward: Upload Parameter Updates
    ax.annotate("", xy=(27, 57.5), xytext=(27, 48),
                arrowprops=dict(arrowstyle="->", color=c_up_arrow, lw=2.0, linestyle="dashed"))
    ax.text(29, 52.5, r"$\Delta\theta_1, \Delta\psi_1$", ha="left", va="center", fontsize=8, fontweight="bold", color=c_up_arrow)

    ax.annotate("", xy=(55, 57.5), xytext=(55, 48),
                arrowprops=dict(arrowstyle="->", color=c_up_arrow, lw=2.0, linestyle="dashed"))
    ax.text(57, 52.5, r"$\Delta\theta_2, \Delta\psi_2$", ha="left", va="center", fontsize=8, fontweight="bold", color=c_up_arrow)

    ax.annotate("", xy=(83, 57.5), xytext=(83, 48),
                arrowprops=dict(arrowstyle="->", color=c_up_arrow, lw=2.0, linestyle="dashed"))
    ax.text(85, 52.5, r"$\Delta\theta_K, \Delta\psi_K$", ha="left", va="center", fontsize=8, fontweight="bold", color=c_up_arrow)

    # 2. Hospital Client Nodes (Bottom Row)
    # Hospital 1
    h1_rect = patches.FancyBboxPatch((5, 5), 28, 42, boxstyle="round,pad=0.6,rounding_size=2",
                                     facecolor=c_client_bg, edgecolor=c_h1_border, linewidth=2.2)
    ax.add_patch(h1_rect)
    ax.text(19, 43.5, "HOSPITAL 1 (Tertiary Center)", ha="center", va="center", fontsize=10, fontweight="bold", color=c_h1_border)
    ax.text(19, 40.5, "Hardware: Siemens CT Fleet | High IPF", ha="center", va="center", fontsize=7.5, color="#666666")

    # H1 components
    ax.text(19, 35.5, "• Local Private Dataset:", ha="center", va="center", fontsize=8.5, fontweight="bold", color=c_text_dark)
    ax.text(19, 32.0, "33 IPF | 72 COPD | 296 Normal", ha="center", va="center", fontsize=8, color="#1A5FB4")
    ax.text(19, 26.5, "• Stage 1: Generator Distillation", ha="center", va="center", fontsize=8.5, fontweight="bold", color=c_text_dark)
    ax.text(19, 23.0, "Matches Real IPF Feature Centroids", ha="center", va="center", fontsize=7.8, color="#27AE60")
    ax.text(19, 17.5, "• Stage 2: Local Replay Training", ha="center", va="center", fontsize=8.5, fontweight="bold", color=c_text_dark)
    ax.text(19, 13.0, "Classifier Trained on Real + Synthetic\nBatches: " + r"$f_{\text{comb}} = [f_{\text{real}}, \hat{f}_{\text{IPF}}]$",
            ha="center", va="center", fontsize=7.5, color="#333333")

    # Hospital 2 (Zero IPF)
    h2_rect = patches.FancyBboxPatch((36, 5), 28, 42, boxstyle="round,pad=0.6,rounding_size=2",
                                     facecolor="#FFF9F5", edgecolor=c_h2_border, linewidth=2.2)
    ax.add_patch(h2_rect)
    ax.text(50, 43.5, "HOSPITAL 2 (Community Clinic)", ha="center", va="center", fontsize=10, fontweight="bold", color=c_h2_border)
    ax.text(50, 40.5, "Hardware: GE Scanner | 0 IPF Patients!", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#D35400")

    # H2 components
    ax.text(50, 35.5, "• Local Private Dataset:", ha="center", va="center", fontsize=8.5, fontweight="bold", color=c_text_dark)
    ax.text(50, 32.0, "0 IPF | 21 COPD | 0 Normal", ha="center", va="center", fontsize=8, fontweight="bold", color="#C0392B")
    ax.text(50, 26.5, "• SOTA FedIIC Failure Point:", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#C0392B")
    ax.text(50, 23.0, "DALA Prior log(0) → -inf (Collapses!)", ha="center", va="center", fontsize=7.8, color="#C0392B")
    ax.text(50, 17.5, "• FedGen-Rare Generative Replay:", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#27AE60")
    ax.text(50, 13.0, r"$\mathcal{G}_\psi$ Synthesizes 100% of Rare Signal!" + "\nLocally Trains IPF Decision Boundary",
            ha="center", va="center", fontsize=7.5, fontweight="bold", color="#27AE60")

    # Hospital K (1 IPF Case)
    hk_rect = patches.FancyBboxPatch((67, 5), 28, 42, boxstyle="round,pad=0.6,rounding_size=2",
                                     facecolor=c_client_bg, edgecolor=c_hk_border, linewidth=2.2)
    ax.add_patch(hk_rect)
    ax.text(81, 43.5, "HOSPITAL K (Rural Center)", ha="center", va="center", fontsize=10, fontweight="bold", color=c_hk_border)
    ax.text(81, 40.5, "Hardware: Philips Scanner | 1 IPF Patient", ha="center", va="center", fontsize=7.5, color="#666666")

    # HK components
    ax.text(81, 35.5, "• Local Private Dataset:", ha="center", va="center", fontsize=8.5, fontweight="bold", color=c_text_dark)
    ax.text(81, 32.0, "1 IPF | 142 COPD | 0 Normal", ha="center", va="center", fontsize=8, color="#8E44AD")
    ax.text(81, 26.5, "• SOTA FedIIC Failure Point:", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#C0392B")
    ax.text(81, 23.0, "IntraSCL has 0 Positive Pairs! (Collapses)", ha="center", va="center", fontsize=7.8, color="#C0392B")
    ax.text(81, 17.5, "• FedGen-Rare Generative Replay:", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#27AE60")
    ax.text(81, 13.0, "Generates Positive Anchors for IPF\nPrevents Majority COPD Drowning",
            ha="center", va="center", fontsize=7.5, color="#333333")

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Rendered high-resolution system architecture diagram to {output_path}")

if __name__ == "__main__":
    render_system_architecture()
