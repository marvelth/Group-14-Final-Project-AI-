"""
Hasil evaluasi model KNN

Output grafik otomatis tersimpan ke model/evaluation_charts/
    1. accuracy_by_k.png         - Top-1 & Top-3 accuracy across K values
    2. crossval_scores.png       - 5-Fold Cross Validation per-fold accuracy
    3. per_class_f1.png          - Per-class F1-score for all 30 majors
    4. confusion_matrix.png      - Confusion matrix heatmap (test set, K=7)
    5. field_accuracy.png        - Average accuracy grouped by academic field
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, precision_score, recall_score, f1_score
)

# ── Path Setup ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from model.knn_model import EduPathKNNModel

# ── Chart Output Directory ────────────────────────────────────────────────────
CHART_DIR = BASE_DIR / 'model' / 'evaluation_charts'
CHART_DIR.mkdir(exist_ok=True)

# ── Color Palette (consistent across all charts) ──────────────────────────────
PALETTE = {
    'primary':    '#6C63FF',   # violet — main bars/lines
    'secondary':  '#48CFAD',   # teal — secondary bars/lines
    'accent':     '#FC6B57',   # coral — highlight / warning
    'bg':         '#1A1A2E',   # dark bg
    'surface':    '#16213E',   # slightly lighter dark
    'text':       '#E0E0E0',   # light text
    'grid':       '#2A2A4A',   # subtle grid lines
}

FIELD_COLORS = {
    'Science and Technology':    '#6C63FF',
    'Engineering':               '#48CFAD',
    'Health':                    '#FC6B57',
    'Economics and Business':    '#FFCE54',
    'Social, Law and Governance':'#A29BFE',
    'Education and Creative':    '#FD79A8',
    'Agriculture and Marine':    '#55EFC4',
}

def apply_dark_theme():
    """Apply consistent dark theme to all matplotlib figures."""
    plt.rcParams.update({
        'figure.facecolor':  PALETTE['bg'],
        'axes.facecolor':    PALETTE['surface'],
        'axes.edgecolor':    PALETTE['grid'],
        'axes.labelcolor':   PALETTE['text'],
        'axes.titlecolor':   PALETTE['text'],
        'xtick.color':       PALETTE['text'],
        'ytick.color':       PALETTE['text'],
        'grid.color':        PALETTE['grid'],
        'grid.linestyle':    '--',
        'grid.alpha':        0.6,
        'text.color':        PALETTE['text'],
        'font.family':       'DejaVu Sans',
        'axes.spines.top':   False,
        'axes.spines.right': False,
    })


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER: build top-3 list per test sample
# ══════════════════════════════════════════════════════════════════════════════
def build_top3_lists(clf, train_X, train_y, test_X):
    _, neighbor_idxs = clf.kneighbors(test_X, n_neighbors=3, return_distance=True)
    top3_lists = []
    for idxs in neighbor_idxs:
        labels = train_y[idxs]
        unique_labels = []
        for label in labels:
            if label not in unique_labels:
                unique_labels.append(label)
            if len(unique_labels) >= 3:
                break
        while len(unique_labels) < 3:
            for label in train_y:
                if label not in unique_labels:
                    unique_labels.append(label)
                    break
        top3_lists.append(unique_labels)
    return top3_lists


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 1 — Accuracy by K
# ══════════════════════════════════════════════════════════════════════════════
def chart_accuracy_by_k(train_X, test_X, train_y, test_y):
    print("  [1/5] Generating: accuracy_by_k.png ...")
    k_values = [1, 3, 5, 7, 9, 11, 13]
    top1_accs, top3_accs = [], []

    for k in k_values:
        clf = KNeighborsClassifier(n_neighbors=k, weights='distance', metric='euclidean')
        clf.fit(train_X, train_y)
        preds = clf.predict(test_X)
        top3 = build_top3_lists(clf, train_X, train_y, test_X)

        top1_accs.append(np.mean(preds == test_y) * 100)
        top3_accs.append(np.mean([test_y[i] in top3[i] for i in range(len(test_y))]) * 100)

    apply_dark_theme()
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.suptitle('KNN Accuracy vs. Number of Neighbors (K)', fontsize=14, fontweight='bold', y=1.01)

    ax.plot(k_values, top1_accs, marker='o', linewidth=2.5, markersize=8,
            color=PALETTE['primary'], label='Top-1 Accuracy')
    ax.plot(k_values, top3_accs, marker='s', linewidth=2.5, markersize=8,
            color=PALETTE['secondary'], label='Top-3 Accuracy', linestyle='--')

    # Highlight K=7 (default)
    idx7 = k_values.index(7)
    ax.axvline(x=7, color=PALETTE['accent'], linestyle=':', linewidth=1.5, alpha=0.7)
    ax.annotate(f'Default K=7\n({top1_accs[idx7]:.1f}% / {top3_accs[idx7]:.1f}%)',
                xy=(7, top1_accs[idx7]),
                xytext=(8.2, top1_accs[idx7] - 1.8),
                fontsize=9, color=PALETTE['accent'],
                arrowprops=dict(arrowstyle='->', color=PALETTE['accent'], lw=1.2))

    for i, k in enumerate(k_values):
        ax.text(k, top1_accs[i] + 0.3, f'{top1_accs[i]:.1f}%', ha='center', fontsize=7.5,
                color=PALETTE['primary'])
        ax.text(k, top3_accs[i] - 1.0, f'{top3_accs[i]:.1f}%', ha='center', fontsize=7.5,
                color=PALETTE['secondary'])

    ax.set_xlabel('K (Number of Neighbors)', fontsize=11)
    ax.set_ylabel('Accuracy (%)', fontsize=11)
    ax.set_xticks(k_values)
    ax.set_ylim(80, 101)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    ax.legend(fontsize=10, framealpha=0.2)
    ax.grid(True, axis='y')

    plt.tight_layout()
    out = CHART_DIR / 'accuracy_by_k.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=PALETTE['bg'])
    plt.close()
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 2 — 5-Fold Cross Validation
# ══════════════════════════════════════════════════════════════════════════════
def chart_crossval(X, y):
    print("  [2/5] Generating: crossval_scores.png ...")
    clf = KNeighborsClassifier(n_neighbors=7, weights='distance', metric='euclidean')
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X, y, cv=cv, scoring='accuracy') * 100

    apply_dark_theme()
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.suptitle('5-Fold Stratified Cross-Validation (K=7)', fontsize=14, fontweight='bold')

    fold_labels = [f'Fold {i+1}' for i in range(5)]
    bar_colors = [PALETTE['accent'] if s == scores.min() else PALETTE['primary'] for s in scores]
    bars = ax.bar(fold_labels, scores, color=bar_colors, width=0.5, zorder=3, edgecolor='none')

    mean_score = scores.mean()
    std_score = scores.std()
    ax.axhline(mean_score, color=PALETTE['secondary'], linestyle='--', linewidth=2,
               label=f'Mean = {mean_score:.2f}%  (±{std_score:.2f}%)')

    # Fill ±1 std band
    ax.axhspan(mean_score - std_score, mean_score + std_score,
               alpha=0.12, color=PALETTE['secondary'])

    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f'{score:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold',
                color=PALETTE['text'])

    ax.set_ylabel('Accuracy (%)', fontsize=11)
    ax.set_ylim(85, 97)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    ax.legend(fontsize=10, framealpha=0.2)
    ax.grid(True, axis='y', zorder=0)

    plt.tight_layout()
    out = CHART_DIR / 'crossval_scores.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=PALETTE['bg'])
    plt.close()
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 3 — Per-Class F1 Score
# ══════════════════════════════════════════════════════════════════════════════
def chart_per_class_f1(train_X, test_X, train_y, test_y, field_map):
    print("  [3/5] Generating: per_class_f1.png ...")
    clf = KNeighborsClassifier(n_neighbors=7, weights='distance', metric='euclidean')
    clf.fit(train_X, train_y)
    preds = clf.predict(test_X)
    report = classification_report(test_y, preds, output_dict=True)

    classes = sorted(set(test_y))
    f1_scores = [report[c]['f1-score'] * 100 for c in classes]
    bar_colors = [FIELD_COLORS.get(field_map.get(c, ''), PALETTE['primary']) for c in classes]

    sorted_data = sorted(zip(f1_scores, classes, bar_colors), reverse=True)
    f1_sorted, cls_sorted, clr_sorted = zip(*sorted_data)

    apply_dark_theme()
    fig, ax = plt.subplots(figsize=(11, 8))
    fig.suptitle('Per-Class F1-Score — All 30 Majors (K=7)', fontsize=14, fontweight='bold')

    y_pos = np.arange(len(cls_sorted))
    bars = ax.barh(y_pos, f1_sorted, color=clr_sorted, height=0.65, edgecolor='none', zorder=3)

    ax.axvline(np.mean(f1_sorted), color=PALETTE['accent'], linestyle='--', linewidth=1.5,
               label=f'Mean F1 = {np.mean(f1_sorted):.1f}%')

    for bar, score in zip(bars, f1_sorted):
        ax.text(score + 0.5, bar.get_y() + bar.get_height() / 2,
                f'{score:.1f}%', va='center', fontsize=7.5, color=PALETTE['text'])

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cls_sorted, fontsize=8.5)
    ax.set_xlabel('F1-Score (%)', fontsize=11)
    ax.set_xlim(0, 112)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    ax.legend(fontsize=9, framealpha=0.2, loc='lower right')
    ax.grid(True, axis='x', zorder=0)

    # Field color legend
    legend_patches = [mpatches.Patch(color=c, label=f) for f, c in FIELD_COLORS.items()]
    ax.legend(handles=legend_patches + [
        mpatches.Patch(color=PALETTE['accent'], label=f'Mean F1 = {np.mean(f1_sorted):.1f}%',
                       linestyle='--', fill=False)
    ], fontsize=7.5, framealpha=0.15, loc='lower right')

    plt.tight_layout()
    out = CHART_DIR / 'per_class_f1.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=PALETTE['bg'])
    plt.close()
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 4 — Confusion Matrix Heatmap
# ══════════════════════════════════════════════════════════════════════════════
def chart_confusion_matrix(train_X, test_X, train_y, test_y):
    print("  [4/5] Generating: confusion_matrix.png ...")
    clf = KNeighborsClassifier(n_neighbors=7, weights='distance', metric='euclidean')
    clf.fit(train_X, train_y)
    preds = clf.predict(test_X)

    classes = sorted(set(test_y))
    cm = confusion_matrix(test_y, preds, labels=classes)

    apply_dark_theme()
    fig, ax = plt.subplots(figsize=(14, 12))
    fig.suptitle('Confusion Matrix — Test Set (K=7, 600 samples)', fontsize=14, fontweight='bold')

    cmap = sns.color_palette("rocket_r", as_cmap=True)
    sns.heatmap(cm, annot=True, fmt='d', cmap=cmap,
                xticklabels=classes, yticklabels=classes,
                linewidths=0.3, linecolor=PALETTE['bg'],
                ax=ax, cbar_kws={'shrink': 0.75},
                annot_kws={'size': 7})

    ax.set_xlabel('Predicted Label', fontsize=11, labelpad=10)
    ax.set_ylabel('True Label', fontsize=11, labelpad=10)
    ax.tick_params(axis='x', rotation=45, labelsize=7.5)
    ax.tick_params(axis='y', rotation=0, labelsize=7.5)

    plt.tight_layout()
    out = CHART_DIR / 'confusion_matrix.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=PALETTE['bg'])
    plt.close()
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 5 — Accuracy Grouped by Academic Field
# ══════════════════════════════════════════════════════════════════════════════
def chart_field_accuracy(train_X, test_X, train_y, test_y, field_map):
    print("  [5/5] Generating: field_accuracy.png ...")
    clf = KNeighborsClassifier(n_neighbors=7, weights='distance', metric='euclidean')
    clf.fit(train_X, train_y)
    preds = clf.predict(test_X)

    # Group by field
    field_correct = {}
    field_total = {}
    for true, pred in zip(test_y, preds):
        field = field_map.get(true, 'Unknown')
        field_correct[field] = field_correct.get(field, 0) + (1 if true == pred else 0)
        field_total[field] = field_total.get(field, 0) + 1

    fields = list(field_total.keys())
    accuracies = [field_correct[f] / field_total[f] * 100 for f in fields]
    counts = [field_total[f] for f in fields]
    colors = [FIELD_COLORS.get(f, PALETTE['primary']) for f in fields]

    sorted_data = sorted(zip(accuracies, fields, colors, counts), reverse=True)
    acc_s, fld_s, clr_s, cnt_s = zip(*sorted_data)

    apply_dark_theme()
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.suptitle('Top-1 Accuracy Grouped by Academic Field (K=7)', fontsize=14, fontweight='bold')

    x_pos = np.arange(len(fld_s))
    bars = ax.bar(x_pos, acc_s, color=clr_s, width=0.55, edgecolor='none', zorder=3)

    ax.axhline(np.mean(acc_s), color=PALETTE['accent'], linestyle='--', linewidth=1.5,
               label=f'Mean = {np.mean(acc_s):.1f}%')

    for bar, acc, n in zip(bars, acc_s, cnt_s):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f'{acc:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold',
                color=PALETTE['text'])
        ax.text(bar.get_x() + bar.get_width() / 2, 1,
                f'n={n}', ha='center', va='bottom', fontsize=7.5, color='#888888')

    short_labels = [f.replace(' and ', ' &\n').replace(', ', '\n& ') for f in fld_s]
    ax.set_xticks(x_pos)
    ax.set_xticklabels(short_labels, fontsize=8.5, ha='center')
    ax.set_ylabel('Accuracy (%)', fontsize=11)
    ax.set_ylim(0, 105)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    ax.legend(fontsize=10, framealpha=0.2)
    ax.grid(True, axis='y', zorder=0)

    plt.tight_layout()
    out = CHART_DIR / 'field_accuracy.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=PALETTE['bg'])
    plt.close()
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("  EduPath AI — KNN Model Evaluation")
    print("=" * 60)

    # ── Load model & data ────────────────────────────────────────
    print("\n[SETUP] Loading model and dataset...")
    csv_path   = str(BASE_DIR / 'model' / 'major_profile.csv')
    synth_path = str(BASE_DIR / 'model' / 'synthetic_dataset.csv')
    model = EduPathKNNModel(csv_path=csv_path, synthetic_data_path=synth_path)

    X = model.normalized_synthetic
    y = np.array(model.synthetic_labels)
    field_map = model.base_df.set_index('major')['field'].to_dict()

    print(f"  Total samples  : {len(X)}")
    print(f"  Total classes  : {len(np.unique(y))} majors")
    print(f"  Feature dims   : {X.shape[1]} (8 academic + 6 RIASEC)")

    train_X, test_X, train_y, test_y = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train samples  : {len(train_X)}  |  Test samples: {len(test_X)}")

    # ── Core metrics (K=7) ───────────────────────────────────────
    print("\n[METRICS] Computing metrics for K=7 (default)...")
    clf7 = KNeighborsClassifier(n_neighbors=7, weights='distance', metric='euclidean')
    clf7.fit(train_X, train_y)
    preds7 = clf7.predict(test_X)
    top3_7 = build_top3_lists(clf7, train_X, train_y, test_X)

    top1_acc   = accuracy_score(test_y, preds7) * 100
    top3_acc   = np.mean([test_y[i] in top3_7[i] for i in range(len(test_y))]) * 100
    macro_prec = precision_score(test_y, preds7, average='macro', zero_division=0) * 100
    macro_rec  = recall_score(test_y, preds7, average='macro', zero_division=0) * 100
    macro_f1   = f1_score(test_y, preds7, average='macro', zero_division=0) * 100
    weighted_f1= f1_score(test_y, preds7, average='weighted', zero_division=0) * 100

    print(f"\n  {'Metric':<25} {'Value':>10}")
    print(f"  {'-'*37}")
    print(f"  {'Top-1 Accuracy':<25} {top1_acc:>9.2f}%")
    print(f"  {'Top-3 Accuracy':<25} {top3_acc:>9.2f}%")
    print(f"  {'Macro Precision':<25} {macro_prec:>9.2f}%")
    print(f"  {'Macro Recall':<25} {macro_rec:>9.2f}%")
    print(f"  {'Macro F1-Score':<25} {macro_f1:>9.2f}%")
    print(f"  {'Weighted F1-Score':<25} {weighted_f1:>9.2f}%")

    # ── K sweep ──────────────────────────────────────────────────
    print(f"\n[K SWEEP] Top-1 & Top-3 Accuracy across K values:")
    print(f"  {'K':<6} | {'Top-1':>8} | {'Top-3':>8}")
    print(f"  {'-'*30}")
    for k in [1, 3, 5, 7, 9, 11, 13]:
        clf = KNeighborsClassifier(n_neighbors=k, weights='distance', metric='euclidean')
        clf.fit(train_X, train_y)
        p = clf.predict(test_X)
        t3 = build_top3_lists(clf, train_X, train_y, test_X)
        t1 = np.mean(p == test_y) * 100
        t3a = np.mean([test_y[i] in t3[i] for i in range(len(test_y))]) * 100
        marker = " ◄ default" if k == 7 else ""
        print(f"  K={k:<4} | {t1:>7.2f}% | {t3a:>7.2f}%{marker}")

    # ── Cross Validation ─────────────────────────────────────────
    print(f"\n[CROSS VALIDATION] 5-Fold Stratified CV (K=7):")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    clf_cv = KNeighborsClassifier(n_neighbors=7, weights='distance', metric='euclidean')
    cv_scores = cross_val_score(clf_cv, X, y, cv=cv, scoring='accuracy') * 100
    for i, s in enumerate(cv_scores):
        print(f"  Fold {i+1}: {s:.2f}%")
    print(f"  {'─'*20}")
    print(f"  Mean : {cv_scores.mean():.2f}%")
    print(f"  Std  : ±{cv_scores.std():.2f}%")

    # ── Generate Charts ──────────────────────────────────────────
    print(f"\n[CHARTS] Saving to: {CHART_DIR}")
    chart_accuracy_by_k(train_X, test_X, train_y, test_y)
    chart_crossval(X, y)
    chart_per_class_f1(train_X, test_X, train_y, test_y, field_map)
    chart_confusion_matrix(train_X, test_X, train_y, test_y)
    chart_field_accuracy(train_X, test_X, train_y, test_y, field_map)

    print(f"\n{'='*60}")
    print(f"  Evaluation complete! Charts saved to:")
    print(f"  {CHART_DIR}")
    print(f"    ├── accuracy_by_k.png")
    print(f"    ├── crossval_scores.png")
    print(f"    ├── per_class_f1.png")
    print(f"    ├── confusion_matrix.png")
    print(f"    └── field_accuracy.png")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()