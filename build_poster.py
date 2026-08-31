#!/usr/bin/env python3
"""Build poster HTML, PNG, and PDF for the 4-class mosquito classification paper."""

import glob, json, os, shutil, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(MAIN, "poster.html")
OUT_PNG  = os.path.join(MAIN, "poster_A0.png")
OUT_PDF  = os.path.join(MAIN, "poster_A0.pdf")
ASSETS   = os.path.join(MAIN, "assets")
os.makedirs(ASSETS, exist_ok=True)

def copy_to_assets(src, name):
    dst = os.path.join(ASSETS, name)
    shutil.copy2(src, dst)
    return "assets/" + name

# ─── 4-class balanced subset ───
BALANCED_CLASSES = [
    ("Aedes_albopictus",       "Aedes albopictus",     500),
    ("Culex_pipiens",          "Culex pipiens",        500),
    ("Aedes_aegypti",          "Aedes aegypti",        500),
    ("Culex_quinquefasciatus", "Cx. quinquefasciatus", 500),
]

# ─── Species photos → assets/ ───
dataset_dir = os.path.join(ROOT, "dataset", "sample_images")
photo_cells = []
for i, (folder, display, count) in enumerate(BALANCED_CLASSES):
    best = os.path.join(dataset_dir, folder, "best_poster.jpg")
    fallback = sorted(glob.glob(os.path.join(dataset_dir, folder, "*.jpg")))[0]
    img = best if os.path.exists(best) else fallback
    src = copy_to_assets(img, f"photo_{i}.jpg")
    photo_cells.append(
        f'<div class="ph"><img src="{src}" alt="{display}"/>'
        f'<div class="phname">{display}</div><div class="phcount">n = {count:,}</div></div>'
    )
photo_strip = "\n".join(photo_cells)

# ─── Figures → assets/ ───
fig_map = {
    "fig3": "fig3_pipeline_flowchart.png",
    "fig4": "fig4_training_accuracy.png",
    "fig5": "fig5_validation_accuracy.png",
    "fig6": "fig6_training_loss.png",
    "fig7": "fig7_validation_loss.png",
    "fig8": "fig8_test_accuracy_comparison.png",
    "fig9": "fig9_training_time_comparison.png",
}
fig_paths = {}
for key, fname in fig_map.items():
    fig_paths[key] = copy_to_assets(os.path.join(MAIN, "figures", fname), fname)

# ─── Table data (4-class results) ───
models = [
    ("ResNet50",         69.87, 77.67, 68.44, 76.53, 0.9601),
    ("EfficientNetV2-S", 86.33, 92.00, 85.96, 91.93, 0.9932),
    ("VGG16",            52.67, 83.33, 42.88, 82.97, 0.9620),
]
table_rows = []
for name, b_acc, f_acc, b_f1, f_f1, auc in models:
    hl = ' class="hl"' if name == "EfficientNetV2-S" else ""
    table_rows.append(
        f'<tr{hl}><td>{name}</td>'
        f'<td>{b_acc:.2f}%</td><td>{f_acc:.2f}%</td>'
        f'<td>{b_f1:.2f}%</td><td>{f_f1:.2f}%</td>'
        f'<td>{auc:.4f}</td></tr>'
    )
table_html = "\n".join(table_rows)

# ─── Legend SVGs ───
legend_svg = '''<svg width="2000" height="160" viewBox="0 0 2000 160" xmlns="http://www.w3.org/2000/svg" font-family="Avenir Next, Arial">
<g font-size="38" font-weight="600">
  <line x1="0" y1="70" x2="60" y2="70" stroke="#3B7CB8" stroke-width="6"/>
  <circle cx="30" cy="70" r="7" fill="#3B7CB8"/><text x="76" y="82" fill="#3E2F23">ResNet50</text>
  <line x1="320" y1="70" x2="380" y2="70" stroke="#2AA198" stroke-width="6"/>
  <circle cx="350" cy="70" r="7" fill="#2AA198"/><text x="396" y="82" fill="#3E2F23">EfficientNetV2-S</text>
  <line x1="760" y1="70" x2="820" y2="70" stroke="#6C4C9A" stroke-width="6"/>
  <circle cx="790" cy="70" r="7" fill="#6C4C9A"/><text x="836" y="82" fill="#3E2F23">VGG16</text>
  <rect x="1100" y="50" width="50" height="4" rx="2" fill="#555"/><text x="1170" y="82" fill="#3E2F23">Baseline</text>
  <rect x="1360" y="50" width="50" height="4" rx="2" fill="#555" stroke-dasharray="12 6"/><text x="1430" y="82" fill="#3E2F23">Fine-Tuned</text>
</g></svg>'''

bar_legend_svg = '''<svg width="900" height="100" viewBox="0 0 900 100" xmlns="http://www.w3.org/2000/svg" font-family="Avenir Next, Arial">
<g font-size="36" font-weight="600">
  <rect x="0" y="30" width="40" height="28" rx="4" fill="#D9A66C" stroke="#4A2E1E" stroke-width="2"/>
  <text x="56" y="54" fill="#3E2F23">Baseline</text>
  <rect x="240" y="30" width="40" height="28" rx="4" fill="#8B5E3C" stroke="#4A2E1E" stroke-width="2"/>
  <text x="296" y="54" fill="#3E2F23">Fine-Tuned</text>
</g></svg>'''

# ─── Flowchart SVG (themed, U-shaped) ───
def rounded_rect(x, y, w, h, r, fill, stroke="#D9C6B2"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="3"/>')

def arrow_down(cx, y1, y2, color="#8B5E3C"):
    a, h = 22, 28
    le = y2 - h
    return (f'<line x1="{cx}" y1="{y1}" x2="{cx}" y2="{le}" '
            f'stroke="{color}" stroke-width="8" stroke-linecap="round"/>'
            f'<polygon points="{cx-a},{le} {cx+a},{le} {cx},{y2}" fill="{color}"/>')

def arrow_right(x1, y, x2, color="#8B5E3C"):
    a, w = 22, 28
    le = x2 - w
    return (f'<line x1="{x1}" y1="{y}" x2="{le}" y2="{y}" '
            f'stroke="{color}" stroke-width="8" stroke-linecap="round"/>'
            f'<polygon points="{le},{y-a} {le},{y+a} {x2},{y}" fill="{color}"/>')

def arrow_up(cx, y1, y2, color="#8B5E3C"):
    a, h = 22, 28
    ab = y2 + h
    return (f'<line x1="{cx}" y1="{y1}" x2="{cx}" y2="{ab}" '
            f'stroke="{color}" stroke-width="8" stroke-linecap="round"/>'
            f'<polygon points="{cx-a},{ab} {cx+a},{ab} {cx},{y2}" fill="{color}"/>')

bw, bh = 420, 160
bx_left, bx_right = 40, 580
cx_left, cx_right = bx_left + bw/2, bx_right + bw/2
gap = 50

c_dark, c_mid, c_accent, c_light, c_green = "#4A2E1E", "#8B5E3C", "#C97D4A", "#D9A66C", "#6B8E4E"

y1 = 0
y2 = y1 + bh + gap
y3 = y2 + bh + gap
y4 = y3 + bh + gap
y5, y6, y7, y8 = y4, y4 - bh - gap, y4 - 2*(bh + gap), y4 - 3*(bh + gap)

flowchart_svg = f'''<svg width="1040" height="1000" viewBox="0 0 1040 1000"
     xmlns="http://www.w3.org/2000/svg" font-family="Avenir Next, Arial">
{rounded_rect(bx_left, y1, bw, bh, 18, c_dark)}
<text x="{cx_left}" y="{y1+70}" text-anchor="middle" font-size="32" font-weight="bold" fill="#FFF">AMID V1 Dataset</text>
<text x="{cx_left}" y="{y1+110}" text-anchor="middle" font-size="26" fill="#E8D5C0">8 species &bull; 31,999 images</text>
{arrow_down(cx_left, y1+bh, y2)}
{rounded_rect(bx_left, y2, bw, bh, 18, c_accent)}
<text x="{cx_left}" y="{y2+70}" text-anchor="middle" font-size="32" font-weight="bold" fill="#FFF">Class Balancing</text>
<text x="{cx_left}" y="{y2+110}" text-anchor="middle" font-size="26" fill="#FFF">4 classes &times; 500 each</text>
{arrow_down(cx_left, y2+bh, y3)}
{rounded_rect(bx_left-10, y3-10, bw+20, bh+20, 22, c_green, "#4A6B35")}
<text x="{cx_left}" y="{y3+75}" text-anchor="middle" font-size="34" font-weight="bold" fill="#FFF">Balanced Subset</text>
<text x="{cx_left}" y="{y3+118}" text-anchor="middle" font-size="26" fill="#E8F0E0">2,000 images &bull; 4 classes</text>
{arrow_down(cx_left, y3+bh, y4)}
{rounded_rect(bx_left, y4, bw, bh, 18, c_mid)}
<text x="{cx_left}" y="{y4+70}" text-anchor="middle" font-size="32" font-weight="bold" fill="#FFF">Preprocessing</text>
<text x="{cx_left}" y="{y4+110}" text-anchor="middle" font-size="26" fill="#E8D5C0">Resize &bull; Normalize</text>
{arrow_right(bx_left+bw, y4+bh/2, bx_right)}
{rounded_rect(bx_right, y5, bw, bh, 18, c_mid)}
<text x="{cx_right}" y="{y5+70}" text-anchor="middle" font-size="32" font-weight="bold" fill="#FFF">Augmentation</text>
<text x="{cx_right}" y="{y5+110}" text-anchor="middle" font-size="26" fill="#E8D5C0">Flip &bull; Rotate &bull; Zoom</text>
{arrow_up(cx_right, y5, y6+bh)}
{rounded_rect(bx_right, y6, bw, bh, 18, c_light)}
<text x="{cx_right}" y="{y6+70}" text-anchor="middle" font-size="32" font-weight="bold" fill="#4A2E1E">Train/Val/Test Split</text>
<text x="{cx_right}" y="{y6+110}" text-anchor="middle" font-size="26" fill="#4A2E1E">70% / 15% / 15%</text>
{arrow_up(cx_right, y6, y7+bh)}
{rounded_rect(bx_right, y7, bw, bh, 18, c_accent)}
<text x="{cx_right}" y="{y7+55}" text-anchor="middle" font-size="30" font-weight="bold" fill="#FFF">3-CNN Benchmarking</text>
<text x="{cx_right}" y="{y7+90}" text-anchor="middle" font-size="24" fill="#FFF">ResNet50 &bull; EfficientNetV2-S</text>
<text x="{cx_right}" y="{y7+120}" text-anchor="middle" font-size="24" fill="#FFF">VGG16</text>
{arrow_up(cx_right, y7, y8+bh)}
{rounded_rect(bx_right, y8, bw, bh, 18, c_dark)}
<text x="{cx_right}" y="{y8+70}" text-anchor="middle" font-size="32" font-weight="bold" fill="#FFF">Comparative Results</text>
<text x="{cx_right}" y="{y8+110}" text-anchor="middle" font-size="26" fill="#E8D5C0">Acc &bull; F1 &bull; AUC &bull; Loss</text>
</svg>'''

# ─── HTML Template ───
HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<style>
@page { size: 841mm 1189mm; margin: 0; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { background: #8B5E3C; }
body { font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif; color: #3E2F23;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.poster { width: 4967px; height: 7022px; background: #F5E9DD; border: 58px solid #8B5E3C;
          padding: 56px 72px 60px 72px; overflow: hidden; display: flex; flex-direction: column; }
.header { text-align: center; }
.title { font-size: 126px; font-weight: 700; color: #4A2E1E; letter-spacing: 1px; line-height: 1.14; }
.authors { font-size: 44px; font-style: italic; color: #3E2F23; margin-top: 36px; }
.affil { font-size: 40px; color: #6B4F3A; margin-top: 16px; }
.rule { height: 9px; background: #C97D4A; margin: 44px 0 36px 0; border-radius: 5px; }
.columns { flex: 1; min-height: 0; display: flex; }
.col-left { width: 45%; padding-right: 40px; display: flex; flex-direction: column;
            justify-content: space-between; overflow: hidden; }
.col-right { width: 55%; padding-left: 40px; border-left: 5px dashed #C9A883; display: flex;
             flex-direction: column; justify-content: space-between; overflow: hidden; }
h2 { font-size: 82px; font-weight: 700; color: #4A2E1E; margin: 0 0 14px 0; }
h3 { font-size: 54px; font-weight: 700; color: #4A2E1E; margin: 0 0 12px 0; }
p, li { font-size: 42px; line-height: 1.38; color: #3E2F23; text-align: justify; }
ul { padding-left: 50px; }
li { margin-bottom: 10px; }
.box { background: #EFDCC5; border-radius: 28px; padding: 30px 36px; }
.aim { border: 6px solid #C97D4A; text-align: center; }
.aim b { color: #A0522D; }
.divider { border-top: 5px dashed #C9A883; margin: 22px 0; }
.datasettitle { font-size: 40px; font-weight: 700; color: #4A2E1E; text-align: center; margin-bottom: 18px; }
.photogrid { display: flex; flex-wrap: wrap; gap: 14px; justify-content: center; }
.ph { width: 820px; text-align: center; }
.ph img { width: 820px; height: 260px; object-fit: cover; border-radius: 14px; border: 3px solid #C9A883; display: block; }
.phname { font-size: 32px; font-weight: 600; color: #4A2E1E; margin-top: 8px; }
.phcount { font-size: 30px; color: #A0522D; font-weight: 600; }
.figbox { padding: 36px 32px 28px 32px; }
.figbox img.flowchart { width: 100%; height: auto; display: block; }
.caption { font-size: 36px; color: #6B4F3A; margin: 22px 8px 0 8px; line-height: 1.36; }
.caption b { color: #4A2E1E; }
.charttitle { font-size: 46px; font-weight: 700; color: #4A2E1E; text-align: center; margin: 20px 0 6px 0; }
table { width: 100%; border-collapse: collapse; margin-top: 24px; }
th { background: #4A2E1E; color: #F5E9DD; font-size: 40px; font-weight: 700; padding: 24px 14px; text-align: center; }
th:first-child { border-radius: 16px 0 0 0; } th:last-child { border-radius: 0 16px 0 0; }
td { font-size: 38px; padding: 22px 14px; text-align: center; border-bottom: 2px solid #D8C3AC; color: #3E2F23; }
td:first-child { font-weight: 600; text-align: left; padding-left: 30px; }
tr.hl td { background: #F6D9A8; font-weight: 700; color: #4A2E1E; }
.refs { font-size: 32px; line-height: 1.40; color: #4A382B; }
.refs li { margin-bottom: 12px; }
.bottomrow { display: flex; gap: 40px; align-items: stretch; }
.refsbox { flex: 1; padding: 36px 42px; }
.qrbox { width: 520px; background: #2B211A; border-radius: 28px; display: flex; flex-direction: column;
         align-items: center; justify-content: center; padding: 32px; }
.qrbox .qr-placeholder { width: 360px; height: 360px; border: 4px dashed #6B4F3A; border-radius: 18px;
                          display: flex; align-items: center; justify-content: center;
                          color: #6B4F3A; font-size: 34px; font-weight: 600; text-align: center; }
.qrtext { color: #F5E9DD; font-size: 36px; font-weight: 600; margin-top: 20px; text-align: center; }
.curves-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }
.curves-grid .curve-cell { background: #F5E9DD; border-radius: 14px; border: 3px solid #C9A883; overflow: hidden; }
.curves-grid .curve-cell img { width: 100%; height: auto; display: block; mix-blend-mode: multiply; }
.curve-label { font-size: 32px; font-weight: 600; color: #4A2E1E; text-align: center; padding: 6px 0 2px 0; }
.barchart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }
.barchart-grid .bc-cell { background: #F5E9DD; border-radius: 14px; border: 3px solid #C9A883; overflow: hidden; }
.barchart-grid .bc-cell img { width: 100%; height: auto; display: block; mix-blend-mode: multiply; }
.bc-label { font-size: 32px; font-weight: 600; color: #4A2E1E; text-align: center; padding: 6px 0 2px 0; }
</style></head><body>
<div class="poster">
  <div class="header">
    <div class="title">MOSQUITO SPECIES CLASSIFICATION FOR DISEASE PREVENTION: A BANGLADESHI DATASET STUDY</div>
    <div class="authors">Azim Pial (2023200000601) &bull; Naima Sultana (2023200000636) &bull; Wahid Imtiaz Arnob (2023200000616) &bull; Md. Shahadat Hossan (2023200000599)</div>
    <div class="affil">Department of Computer Science &amp; Engineering, Southeast University, Dhaka, Bangladesh</div>
    <div class="affil" style="margin-top:10px; font-style:italic;">Supervisor: Mahdin Mahboob, Assistant Professor, CSE, Southeast University</div>
    <div class="rule"></div>
  </div>
  <div class="columns">
    <div class="col-left">
      <div>
        <h2>Introduction</h2>
        <p>In recent years, mosquito-borne diseases have become an increasingly serious global health problem. Of more than 3,700 mosquito species worldwide, only a small subset act as disease vectors. However, this small group account for most vector-borne infections: Aedes mosquitoes commonly transmit dengue, Anopheles transport malaria, and Culex linked to West Nile and other viral diseases. The WHO reported over 14.4 million dengue cases globally in 2024, while the World Malaria Report 2025 estimated 282 million malaria cases and roughly 610,000 deaths worldwide. The country experienced its worst dengue outbreak in 2023, with 321,179 reported cases and 1,705 deaths [3]. In addition to spending at least Tk5,476 crore annually on mosquito prevention, Bangladesh faces high dengue treatment costs averaging BDT 33,817 per household, alongside BDT 6,076 per patient spent directly by public hospitals.</p>
      </div>
      <div>
        <h2>Problem Statement</h2>
        <p>Timely, accurate species identification is essential for disease prevention and localized vector control. However, following traditional identification, even trained experts misidentify adult mosquitoes roughly 18% of the time [4]. Similarly, DNA-based techniques improve accuracy but require expensive laboratory infrastructure. Convolutional Neural Networks (CNNs) offer a scalable, cost-effective alternative for species recognition, but most studies rely on generic and foreign datasets that do not reflect the distinct morphological and ecological characteristics of Bangladeshi mosquito populations.</p>
      </div>
      <div class="box">
        <div class="datasettitle">AMID&nbsp;V1 Balanced Subset &mdash; 2,000 images &middot; 4 classes &middot; 500 per class</div>
        <div class="photogrid">%%PHOTO_STRIP%%</div>
      </div>
      <div class="box aim"><p><b>Aim:</b> Benchmark four CNN architectures on a <b>balanced 4-class subset</b> of the AMID&nbsp;V1 Bangladeshi mosquito dataset and demonstrate that careful class selection and dataset balancing are critical for reliable species-level classification.</p></div>
      <div>
        <div class="divider"></div>
        <h2>Methods</h2>
        <p>Three ImageNet-pretrained CNN backbones &mdash; ResNet50, EfficientNetV2-S, and VGG16 &mdash; were fine-tuned on a balanced 2,000-image AMID&nbsp;V1 subset (4 classes, 500 each) using stratified 70/15/15 train&ndash;validation&ndash;test splits on Google Colab.</p>
        <h3 style="margin-top:22px">Protocol</h3>
        <ul>
          <li>Two-stage transfer learning: frozen backbone &rarr; partial unfreeze with cosine decay LR</li>
          <li>Data augmentation: flip, rotate, zoom, brightness adjustment</li>
          <li>Metrics: Accuracy, Macro Precision, Recall, F1, ROC-AUC</li>
        </ul>
      </div>
      <div>
        <div class="box figbox" style="text-align:center">
          <img class="flowchart" src="%%FIG3%%" alt="Pipeline Flowchart"/>
          <div class="caption"><b>Figure 1:</b> End-to-end pipeline from dataset acquisition through balancing, preprocessing, and three-architecture benchmarking to comparative evaluation.</div>
        </div>
      </div>
    </div>
    <div class="col-right">
      <div>
        <h2>Result</h2>
        <p>Among the three architectures evaluated on the balanced 4-class AMID V1 dataset, fine-tuned EfficientNetV2-S achieved the best overall performance, with test accuracy reaching 92.00% and macro-F1 at 91.93%. VGG16 showed the most dramatic improvement, with test accuracy rising from 52.67% baseline to 83.33% after fine-tuning and macro-F1 improving from 42.88% to 82.97%. ResNet50 achieved 77.67% accuracy with strong ROC-AUC of 96.01% but the least gain from fine-tuning.</p>
      </div>
      <div>
        <div class="charttitle">Training &amp; Validation Curves</div>
        <div style="text-align:center; margin-bottom:8px">%%LEGEND_SVG%%</div>
        <div class="curves-grid">
          <div class="curve-cell"><img src="%%FIG4%%" alt="Training Accuracy"/><div class="curve-label">(a) Training Accuracy</div></div>
          <div class="curve-cell"><img src="%%FIG5%%" alt="Validation Accuracy"/><div class="curve-label">(b) Validation Accuracy</div></div>
          <div class="curve-cell"><img src="%%FIG6%%" alt="Training Loss"/><div class="curve-label">(c) Training Loss</div></div>
          <div class="curve-cell"><img src="%%FIG7%%" alt="Validation Loss"/><div class="curve-label">(d) Validation Loss</div></div>
        </div>
        <div class="caption"><b>Figure 2:</b> Baseline (epochs 1&ndash;10) and fine-tuned (epochs 11+) phases. Solid = baseline, dashed = fine-tuned.</div>
      </div>
      <div>
        <div class="charttitle">Accuracy &amp; Training Time Comparison</div>
        <div style="text-align:center; margin-bottom:8px">%%BAR_LEGEND_SVG%%</div>
        <div class="barchart-grid">
          <div class="bc-cell"><img src="%%FIG8%%" alt="Test Accuracy"/><div class="bc-label">(e) Test Accuracy</div></div>
          <div class="bc-cell"><img src="%%FIG9%%" alt="Training Time"/><div class="bc-label">(f) Training Time</div></div>
        </div>
        <div class="caption"><b>Figure 3:</b> (e) EfficientNetV2-S achieves the highest fine-tuned accuracy at 92.0%. (f) All models trained in under 71 minutes total.</div>
      </div>
      <div>
        <div class="charttitle">Classification Performance Summary</div>
        <table>
          <tr><th>Model</th><th>Base&nbsp;Acc.</th><th>FT&nbsp;Acc.</th><th>Base&nbsp;F1</th><th>FT&nbsp;F1</th><th>AUC</th></tr>
          %%TABLE_ROWS%%
        </table>
        <div class="caption"><b>Table 1:</b> Baseline (B) vs. Fine-Tuned (FT). EfficientNetV2-S achieves highest accuracy and macro-F1 after fine-tuning.</div>
      </div>
      <div>
        <h2>Limitation/Future Work</h2>
        <ul>
          <li>The study was limited to only four species from a single dataset (AMID V1); cross-dataset generalization remains untested.</li>
          <li>Computational resources restricted experiments to three architectures; deeper models were not explored.</li>
          <li>Explore focal loss, class-weighted loss, and oversampling to handle imbalance</li>
          <li>Develop lightweight architectures for on-device deployment in smart traps</li>
          <li>Extend to multi-modal surveillance: image + acoustic + environmental signals</li>
        </ul>
      </div>
      <div>
        <div class="divider"></div>
        <h2>Conclusion</h2>
        <p>This comparative benchmark advances local disease vector identification through cost-effective, AI-driven surveillance that empowers public health authorities with earlier outbreak detection. Ultimately, it expands the frontier of medical AI innovation by demonstrating how deep learning can tackle high-impact public health challenges in resource-constrained environments.</p>
      </div>
      <div class="bottomrow">
        <div class="box refsbox">
          <h3>References</h3>
          <ol class="refs">
            <li>WHO, &ldquo;Dengue &ndash; global situation,&rdquo; <i>World Health Organization</i>, 2024. [Online]. Available: https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue</li>
            <li>WHO, <i>World Malaria Report 2025</i>. Geneva: World Health Organization, 2025.</li>
            <li>DGHS, Bangladesh, <i>National Dengue Situation Reports 2023</i>. Dhaka: Directorate General of Health Services, 2023.</li>
            <li>T. Balenghien <i>et al.</i>, &ldquo;The current status of mosquito-borne diseases in Europe and the role of mosquitoes as vectors,&rdquo; <i>Parasites &amp; Vectors</i>, vol. 11, no. 1, pp. 1&ndash;12, 2018.</li>
            <li>T. C. Saha, &ldquo;AMID V1: Aedes Mosquito Image Dataset,&rdquo; <i>Kaggle</i>, 2024. [Online]. Available: https://www.kaggle.com/datasets/tonmoy406/aedes-mosquito-image-dataset-version-1-0amid-v1</li>
          </ol>
        </div>
        <div class="qrbox">
          <img src="%%GITHUB_QR%%" style="width:360px;height:360px;border-radius:18px;border:4px solid #6B4F3A;" alt="GitHub Repository QR"/>
          <div class="qrtext">GitHub Repository</div>
        </div>
      </div>
    </div>
  </div>
</div>
</body></html>
"""

# ─── Assemble HTML ───
github_qr = "assets/github_qr.png"
html = (HTML.replace("%%PHOTO_STRIP%%", photo_strip)
            .replace("%%LEGEND_SVG%%", legend_svg)
            .replace("%%BAR_LEGEND_SVG%%", bar_legend_svg)
            .replace("%%FIG3%%", fig_paths["fig3"])
            .replace("%%FIG4%%", fig_paths["fig4"])
            .replace("%%FIG5%%", fig_paths["fig5"])
            .replace("%%FIG6%%", fig_paths["fig6"])
            .replace("%%FIG7%%", fig_paths["fig7"])
            .replace("%%FIG8%%", fig_paths["fig8"])
            .replace("%%FIG9%%", fig_paths["fig9"])
            .replace("%%GITHUB_QR%%", github_qr)
            .replace("%%TABLE_ROWS%%", table_html))

with open(OUT_HTML, "w") as f:
    f.write(html)
print(f"[OK] wrote {OUT_HTML}  ({len(html):,} bytes)")

# ─── Export PNG and PDF via Chrome headless ───
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
file_url = "file://" + os.path.abspath(OUT_HTML)

png_cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           f"--screenshot={OUT_PNG}", "--window-size=4967,7022", file_url]
r = subprocess.run(png_cmd, capture_output=True, text=True, timeout=120)
if os.path.exists(OUT_PNG) and os.path.getsize(OUT_PNG) > 0:
    print(f"[OK] wrote {OUT_PNG}  ({os.path.getsize(OUT_PNG):,} bytes)")
else:
    print(f"[WARN] PNG export may have issues. stderr: {r.stderr[:300]}")

pdf_cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           f"--print-to-pdf={OUT_PDF}", "--print-to-pdf-no-header", file_url]
r = subprocess.run(pdf_cmd, capture_output=True, text=True, timeout=120)
if os.path.exists(OUT_PNG) and os.path.getsize(OUT_PDF) > 0:
    print(f"[OK] wrote {OUT_PDF}  ({os.path.getsize(OUT_PDF):,} bytes)")
else:
    print(f"[WARN] PDF export may have issues. stderr: {r.stderr[:300]}")

print("\nDone! Generated:")
print(f"  - {OUT_HTML}")
print(f"  - {OUT_PNG}")
print(f"  - {OUT_PDF}")
