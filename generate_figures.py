#!/usr/bin/env python3
"""Generate all 9 figures for the 4-class mosquito classification paper."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os, csv, glob, textwrap
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

# ─── Color palette (consistent across all figures) ───
COLORS = {
    "ResNet50":         "#3B7CB8",
    "EfficientNetV2-S": "#2AA198",
    "VGG16":            "#6C4C9A",
}
MARKERS = {"ResNet50": "o", "EfficientNetV2-S": "s", "VGG16": "^"}
model_names = ["ResNet50", "EfficientNetV2-S", "VGG16"]

# ─── New 4-class results ───
# (model, baseline_acc, finetuned_acc, baseline_f1, finetuned_f1, auc, time_min)
results = [
    ("ResNet50",         69.87, 77.67, 68.44, 76.53, 0.9601, 22.64),
    ("EfficientNetV2-S", 86.33, 92.00, 85.96, 91.93, 0.9932, 48.32),
    ("VGG16",            52.67, 83.33, 42.88, 82.97, 0.9620, 50.00),
]

# ─── Training histories ───

# VGG16 (from CSV — 30 baseline + 20 fine-tuned = 50 epochs)
vgg_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "results_VGG16_finetuned.zip")
import zipfile, io
with zipfile.ZipFile(vgg_csv) as z:
    with z.open("results_VGG16/training_history_finetuned.csv") as f:
        reader = csv.DictReader(io.TextIOWrapper(f))
        vgg_rows = list(reader)

vgg_acc = [float(r["accuracy"]) for r in vgg_rows]
vgg_val_acc = [float(r["val_accuracy"]) for r in vgg_rows]
vgg_loss = [float(r["loss"]) for r in vgg_rows]
vgg_val_loss = [float(r["val_loss"]) for r in vgg_rows]
# Baseline = first 30 epochs, Fine-tuned = all 50 epochs
vgg_base_acc = vgg_acc[:30]
vgg_base_val_acc = vgg_val_acc[:30]
vgg_base_loss = vgg_loss[:30]
vgg_base_val_loss = vgg_val_loss[:30]

# ResNet50 (from notebook — 10 frozen + 12 fine-tuned = 22 epochs)
resnet_acc = [0.2907,0.4129,0.4836,0.5243,0.5557,0.5907,0.6286,0.6314,0.6307,0.6279,
              0.6786,0.7236,0.7679,0.7936,0.8186,0.8271,0.8421,0.8629,0.8571,0.8800,0.8800,0.8907]
resnet_val_acc = [0.5000,0.5767,0.6133,0.6067,0.6400,0.6133,0.6333,0.6933,0.6967,0.6933,
                  0.6733,0.7233,0.7233,0.7500,0.7633,0.7767,0.7600,0.7667,0.7367,0.7633,0.7600,0.7833]
resnet_loss = [1.8416,1.4275,1.2569,1.1908,1.1365,1.0704,1.0356,1.0290,1.0044,1.0165,
               0.9298,0.8553,0.7929,0.7603,0.7354,0.7087,0.6770,0.6550,0.6541,0.6328,0.6220,0.6162]
resnet_val_loss = [1.2207,1.0971,1.0326,1.0159,0.9719,0.9891,0.9633,0.9005,0.8943,0.8830,
                   0.9172,0.8522,0.8469,0.7760,0.7695,0.7436,0.8045,0.7825,0.8567,0.7825,0.7896,0.7437]

# EfficientNetV2-S (from notebook — 10 frozen + 30 fine-tuned = 40 epochs)
effnet_acc = [0.3657,0.5586,0.6486,0.7021,0.7500,0.7714,0.7700,0.7871,0.7936,0.8071,
              0.8186,0.8350,0.8457,0.8600,0.8721,0.8879,0.8900,0.8957,0.9014,0.8950,
              0.9107,0.9214,0.9179,0.9243,0.9179,0.9243,0.9321,0.9286,0.9293,0.9279,
              0.9400,0.9286,0.9307,0.9264,0.9329,0.9429,0.9371,0.9279,0.9407,0.9343]
effnet_val_acc = [0.6600,0.7600,0.7900,0.8033,0.8200,0.8267,0.8400,0.8467,0.8533,0.8633,
                  0.8800,0.8933,0.8967,0.9067,0.9067,0.9167,0.9167,0.9133,0.9233,0.9167,
                  0.9300,0.9267,0.9200,0.9233,0.9200,0.9200,0.9233,0.9233,0.9200,0.9200,
                  0.9233,0.9200,0.9233,0.9200,0.9200,0.9200,0.9200,0.9200,0.9200,0.9200]
effnet_loss = [1.3537,1.1279,0.9974,0.9168,0.8473,0.8107,0.7833,0.7679,0.7569,0.7515,
               0.7239,0.6934,0.6832,0.6614,0.6452,0.6214,0.6141,0.6009,0.5911,0.5900,
               0.5754,0.5706,0.5752,0.5611,0.5636,0.5489,0.5468,0.5417,0.5487,0.5397,
               0.5360,0.5417,0.5414,0.5388,0.5416,0.5303,0.5295,0.5393,0.5299,0.5306]
effnet_val_loss = [1.1346,0.9572,0.8507,0.7940,0.7509,0.7340,0.7103,0.6945,0.6806,0.6717,
                   0.6447,0.6281,0.6185,0.6111,0.6045,0.5913,0.5880,0.5816,0.5771,0.5681,
                   0.5738,0.5666,0.5628,0.5617,0.5619,0.5589,0.5593,0.5556,0.5516,0.5507,
                   0.5518,0.5507,0.5502,0.5504,0.5510,0.5504,0.5500,0.5500,0.5499,0.5495]

# Fine-tuning split points (epoch where fine-tuning starts)
FT_EPOCH = {"ResNet50": 10, "EfficientNetV2-S": 10, "VGG16": 30}

# ─── Plot styling ───
plt.rcParams.update({
    "axes.grid": True, "grid.alpha": 0.3,
    "font.size": 11, "axes.labelsize": 12, "axes.titlesize": 13,
    "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "figure.dpi": 300,
})


def _plot_curve(ax, epochs, values, color, marker, label, linestyle="-", markevery=5):
    ax.plot(epochs, values, color=color, linewidth=2.2, label=label,
            linestyle=linestyle, marker=marker, markersize=5, markevery=markevery)


def _add_ft_line(ax, ft_epoch, ymin, ymax):
    ax.axvline(x=ft_epoch, color="#999", linestyle=":", linewidth=1, alpha=0.5)


def _save(fig, name, facecolor="#F5E9DD"):
    fig.savefig(os.path.join(OUT, name), dpi=300, bbox_inches="tight", facecolor=facecolor)
    plt.close(fig)
    print(f"  saved {name}")


# ════════════════════════════════════════════════════════════════════
# FIGURE 1: Class Distribution
# ════════════════════════════════════════════════════════════════════
print("Generating fig1...")
classes = ["Aedes\nalbopictus", "Culex\npipiens", "Aedes\naegypti", "Culex\nquinquefasciatus"]
counts = [500, 500, 500, 500]
bar_colors = ["#3B7CB8", "#2AA198", "#CB4B16", "#6C4C9A"]

fig, ax = plt.subplots(figsize=(10, 5.5))
bars = ax.bar(classes, counts, color=bar_colors, edgecolor="#4A2E1E", linewidth=1.2, width=0.55)
for bar, c in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, str(c),
            ha="center", va="bottom", fontsize=13, fontweight="bold", color="#4A2E1E")
ax.set_ylabel("Number of Images", fontsize=13, fontweight="bold")
ax.set_title("Balanced AMID V1 Subset (2,000 Images) — 500 Images Per Class",
             fontsize=14, fontweight="bold", color="#4A2E1E")
ax.set_ylim(0, 600)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
_save(fig, "fig1_class_distribution.png")


# ════════════════════════════════════════════════════════════════════
# FIGURE 2: Sample Images
# ════════════════════════════════════════════════════════════════════
print("Generating fig2...")
sample_classes = [
    ("Aedes_albopictus", "Aedes albopictus"),
    ("Culex_pipiens", "Culex pipiens"),
    ("Aedes_aegypti", "Aedes aegypti"),
    ("Culex_quinquefasciatus", "Culex quinquefasciatus"),
]

dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "dataset", "sample_images")

fig, axes = plt.subplots(1, 4, figsize=(16, 4.5))
fig.suptitle("Representative Sample Images from the 4-Class Balanced Subset",
             fontsize=14, fontweight="bold", color="#4A2E1E", y=1.02)
for ax, (cls_folder, cls_name) in zip(axes, sample_classes):
    cls_dir = os.path.join(dataset_dir, cls_folder)
    imgs = sorted(glob.glob(os.path.join(cls_dir, "*.jpg")))
    if imgs:
        img = Image.open(imgs[0])
        ax.imshow(np.array(img))
    ax.set_title(cls_name, fontsize=11, fontweight="bold", color="#4A2E1E")
    ax.axis("off")
plt.tight_layout()
_save(fig, "fig2_sample_images.png")


# ════════════════════════════════════════════════════════════════════
# FIGURE 3: Pipeline Flowchart (matplotlib version)
# ════════════════════════════════════════════════════════════════════
print("Generating fig3...")
fig, ax = plt.subplots(figsize=(10, 9), facecolor="#F5E9DD")
ax.set_xlim(0, 10)
ax.set_ylim(-1.4, 9.4)
ax.axis("off")
ax.set_facecolor("#F5E9DD")
ax.set_title("Methodology Pipeline", fontsize=16, fontweight="bold", color="#4A2E1E", pad=16)

# Step boxes: (x, y_center, text, fill, text_color)
steps = [
    (5, 8.6,   "AMID V1 Dataset\n8 species, 31,999 images", "#4A2E1E", "white"),
    (5, 7.3,   "Class Balancing\n4 classes x 500 each", "#C97D4A", "white"),
    (5, 6.0,   "Balanced Subset\n2,000 images, 4 classes", "#6B8E4E", "white"),
    (2.5, 4.7, "Preprocessing\nResize, Normalize", "#8B5E3C", "white"),
    (7.5, 4.7, "Augmentation\nFlip, Rotate, Zoom", "#8B5E3C", "white"),
    (7.5, 3.4, "Train/Val/Test Split\n70% / 15% / 15%", "#D9A66C", "#4A2E1E"),
    (7.5, 2.1, "3-CNN Benchmarking\nResNet50, VGG16", "#C97D4A", "white"),
    (7.5, 0.8, "Fine-tuning\npartial unfreeze", "#6B8E4E", "white"),
    (5, -0.5,  "Comparative Results\nAccuracy, F1, AUC, Loss", "#4A2E1E", "white"),
]

for x, y, text, fc, tc in steps:
    bbox = dict(boxstyle="round,pad=0.28", facecolor=fc, edgecolor="#D9C6B2", linewidth=1.5)
    ax.text(x, y, text, ha="center", va="center", fontsize=9.5, fontweight="bold",
            color=tc, bbox=bbox)

# Arrows drawn between boxes with shrink so they never overlap box edges
arrow_kw = dict(arrowstyle="-|>", color="#8B5E3C", lw=2.2, mutation_scale=22,
                shrinkA=12, shrinkB=12, connectionstyle="arc3,rad=0")
conns = [
    ((5, 8.24), (5, 7.66)),       # 1→2
    ((5, 6.94), (5, 6.36)),       # 2→3
    ((5, 5.64), (2.5, 5.06)),     # 3→4 (down-left)
    ((5, 5.64), (7.5, 5.06)),     # 3→5 (down-right)
    ((2.5, 4.34), (7.5, 4.34)),   # 4→5 (horizontal)
    ((7.5, 4.34), (7.5, 3.76)),   # 5→6
    ((7.5, 3.04), (7.5, 2.46)),   # 6→7
    ((7.5, 1.74), (7.5, 1.16)),   # 7→8
    ((7.5, 0.44), (5, -0.14)),    # 8→9 (down to center)
]
for (x1, y1), (x2, y2) in conns:
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=arrow_kw)

_save(fig, "fig3_pipeline_flowchart.png")


# ════════════════════════════════════════════════════════════════════
# FIGURES 4-7: Training & Validation Curves (2x2 grid)
# ════════════════════════════════════════════════════════════════════
print("Generating fig4-7...")

curve_data = {
    "ResNet50": {
        "acc": resnet_acc, "val_acc": resnet_val_acc,
        "loss": resnet_loss, "val_loss": resnet_val_loss,
        "ft_epoch": 10,
    },
    "EfficientNetV2-S": {
        "acc": effnet_acc, "val_acc": effnet_val_acc,
        "loss": effnet_loss, "val_loss": effnet_val_loss,
        "ft_epoch": 10,
    },
    "VGG16": {
        "acc": vgg_acc, "val_acc": vgg_val_acc,
        "loss": vgg_loss, "val_loss": vgg_val_loss,
        "ft_epoch": 30,
        "base_acc": vgg_base_acc, "base_val_acc": vgg_base_val_acc,
        "base_loss": vgg_base_loss, "base_val_loss": vgg_base_val_loss,
    },
}

titles = ["(a) Training Accuracy", "(b) Validation Accuracy",
          "(c) Training Loss", "(d) Validation Loss"]
ylabels = ["Accuracy", "Accuracy", "Loss", "Loss"]
data_keys = [("acc", "Training Accuracy"), ("val_acc", "Validation Accuracy"),
             ("loss", "Training Loss"), ("val_loss", "Validation Loss")]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Training & Validation Curves — 4-Class Balanced Subset",
             fontsize=15, fontweight="bold", color="#4A2E1E", y=1.01)

for idx, (ax, (key, _)) in enumerate(zip(axes.flat, data_keys)):
    for name in model_names:
        d = curve_data[name]
        vals = d[key]
        epochs = list(range(1, len(vals) + 1))
        color = COLORS[name]
        marker = MARKERS[name]

        # Plot baseline (solid) and fine-tuned (dashed)
        ft = d["ft_epoch"]
        if ft is not None and name == "VGG16":
            # VGG16: baseline = first 30 epochs, fine-tuned = all 50
            base_key = "base_" + key
            if base_key in d:
                base_vals = d[base_key]
                _plot_curve(ax, range(1, len(base_vals)+1), base_vals,
                           color, marker, f"{name} (Baseline)")
                _plot_curve(ax, range(1, len(vals)+1), vals,
                           color, marker, f"{name} (Fine-Tuned)", linestyle="--")
            else:
                _plot_curve(ax, epochs, vals, color, marker, name)
        elif ft is not None:
            base_vals = vals[:ft]
            _plot_curve(ax, range(1, ft+1), base_vals,
                       color, marker, f"{name} (Baseline)")
            _plot_curve(ax, epochs, vals,
                       color, marker, f"{name} (Fine-Tuned)", linestyle="--")
        else:
            _plot_curve(ax, epochs, vals, color, marker, name)

    ax.set_ylabel(ylabels[idx], fontsize=12, fontweight="bold")
    ax.set_title(titles[idx], fontsize=13, fontweight="bold", color="#4A2E1E")
    if idx >= 2:
        ax.set_xlabel("Epoch", fontsize=12, fontweight="bold")

axes[0, 0].legend(loc="lower right", fontsize=8, framealpha=0.9)
plt.tight_layout()
_save(fig, "fig4_training_accuracy.png")

# Split into individual figures for the poster
for idx, (key, title) in enumerate(data_keys):
    fig, ax = plt.subplots(figsize=(8, 5))
    for name in model_names:
        d = curve_data[name]
        vals = d[key]
        epochs = list(range(1, len(vals) + 1))
        color = COLORS[name]
        marker = MARKERS[name]
        ft = d["ft_epoch"]
        if ft is not None and name == "VGG16":
            base_key = "base_" + key
            if base_key in d:
                base_vals = d[base_key]
                _plot_curve(ax, range(1, len(base_vals)+1), base_vals,
                           color, marker, f"{name} (Baseline)")
                _plot_curve(ax, range(1, len(vals)+1), vals,
                           color, marker, f"{name} (Fine-Tuned)", linestyle="--")
        elif ft is not None:
            base_vals = vals[:ft]
            _plot_curve(ax, range(1, ft+1), base_vals,
                       color, marker, f"{name} (Baseline)")
            _plot_curve(ax, epochs, vals,
                       color, marker, f"{name} (Fine-Tuned)", linestyle="--")
        else:
            _plot_curve(ax, epochs, vals, color, marker, name)
    ax.set_xlabel("Epoch", fontsize=12, fontweight="bold")
    ax.set_ylabel(key.replace("_", " ").title().split()[0], fontsize=12, fontweight="bold")
    ax.set_title(title, fontsize=13, fontweight="bold", color="#4A2E1E")
    ax.legend(loc="best", fontsize=9, framealpha=0.9)
    fname_map = {0: "fig4_training_accuracy.png", 1: "fig5_validation_accuracy.png",
                 2: "fig6_training_loss.png", 3: "fig7_validation_loss.png"}
    fname = fname_map[idx]
    _save(fig, fname)


# ════════════════════════════════════════════════════════════════════
# FIGURE 8: Test Accuracy Comparison (bar chart)
# ════════════════════════════════════════════════════════════════════
print("Generating fig8...")
fig, ax = plt.subplots(figsize=(10, 5.5))
x = np.arange(len(model_names))
w = 0.35
base_accs = [r[1] for r in results]
ft_accs = [r[2] for r in results]

bars_b = ax.bar(x - w/2, base_accs, w, label="Baseline", color="#D9A66C", edgecolor="#4A2E1E", linewidth=1.2)
bars_f = ax.bar(x + w/2, ft_accs, w, label="Fine-Tuned", color="#8B5E3C", edgecolor="#4A2E1E", linewidth=1.2)
for bar, val in zip(bars_b, base_accs):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, f"{val:.1f}%",
            ha="center", va="bottom", fontsize=10, fontweight="bold", color="#4A2E1E")
for bar, val in zip(bars_f, ft_accs):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, f"{val:.1f}%",
            ha="center", va="bottom", fontsize=10, fontweight="bold", color="#4A2E1E")
ax.set_xticks(x)
ax.set_xticklabels(model_names, fontsize=12, fontweight="bold", rotation=10, ha="right")
ax.set_ylabel("Test Accuracy (%)", fontsize=12, fontweight="bold")
ax.set_title("Test Accuracy: Baseline vs Fine-Tuned (4-Class)", fontsize=13, fontweight="bold")
ax.set_ylim(0, 105)
ax.legend(fontsize=11)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
_save(fig, "fig8_test_accuracy_comparison.png")


# ════════════════════════════════════════════════════════════════════
# FIGURE 9: Training Time Comparison (bar chart)
# ════════════════════════════════════════════════════════════════════
print("Generating fig9...")
fig, ax = plt.subplots(figsize=(10, 5.5))
times = [r[6] for r in results]
bars = ax.bar(x, times, 0.5, color=["#3B7CB8","#2AA198","#CB4B16","#6C4C9A"],
              edgecolor="#4A2E1E", linewidth=1.2)
for bar, val in zip(bars, times):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.8, f"{val:.1f} min",
            ha="center", va="bottom", fontsize=11, fontweight="bold", color="#4A2E1E")
ax.set_xticks(x)
ax.set_xticklabels(model_names, fontsize=12, fontweight="bold", rotation=10, ha="right")
ax.set_ylabel("Training Time (minutes)", fontsize=12, fontweight="bold")
ax.set_title("Training Time Comparison (4-Class)", fontsize=13, fontweight="bold")
ax.set_ylim(0, max(times) + 12)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
_save(fig, "fig9_training_time_comparison.png")


print(f"\nDone! All figures saved to: {OUT}")
print(f"Files: {sorted(os.listdir(OUT))}")
