import pickle
import matplotlib.pyplot as plt
import numpy as np

# Load training data
with open('training_data.pkl', 'rb') as f:
    training_data = pickle.load(f)

labels = training_data['labels']
normalized_labels = training_data['normalized_labels']

# Create figure with 2 rows x 4 columns (original + normalized)
fig, axes = plt.subplots(2, 4, figsize=(20, 10))

# ============== ORIGINAL LABELS (Top Row) ==============

# 1. Histogram
axes[0, 0].hist(labels, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
axes[0, 0].set_xlabel('Label Value')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('Original Labels - Histogram')
axes[0, 0].grid(True, alpha=0.3)

# 2. Box plot
axes[0, 1].boxplot(labels, vert=True)
axes[0, 1].set_ylabel('Label Value')
axes[0, 1].set_title('Original Labels - Box Plot')
axes[0, 1].grid(True, alpha=0.3)

# 3. Cumulative distribution
sorted_labels = np.sort(labels)
cumulative = np.arange(1, len(sorted_labels) + 1) / len(sorted_labels)
axes[0, 2].plot(sorted_labels, cumulative, color='steelblue')
axes[0, 2].set_xlabel('Label Value')
axes[0, 2].set_ylabel('Cumulative Probability')
axes[0, 2].set_title('Original Labels - CDF')
axes[0, 2].grid(True, alpha=0.3)

# 4. Statistics text
stats_text_original = f"""
Statistics (Original):
---------------------
Total samples: {len(labels):,}
Mean: {np.mean(labels):.3f}
Median: {np.median(labels):.3f}
Std Dev: {np.std(labels):.3f}
Min: {np.min(labels):.3f}
Max: {np.max(labels):.3f}
25th %ile: {np.percentile(labels, 25):.3f}
75th %ile: {np.percentile(labels, 75):.3f}
"""
axes[0, 3].text(0.1, 0.5, stats_text_original, fontsize=11, family='monospace',
                verticalalignment='center')
axes[0, 3].axis('off')
axes[0, 3].set_title('Original Label Statistics')

# ============== NORMALIZED LABELS (Bottom Row) ==============

# 1. Histogram
axes[1, 0].hist(normalized_labels, bins=50, edgecolor='black', alpha=0.7, color='coral')
axes[1, 0].set_xlabel('Normalized Label Value')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].set_title('Normalized Labels - Histogram')
axes[1, 0].grid(True, alpha=0.3)

# 2. Box plot
axes[1, 1].boxplot(normalized_labels, vert=True)
axes[1, 1].set_ylabel('Normalized Label Value')
axes[1, 1].set_title('Normalized Labels - Box Plot')
axes[1, 1].grid(True, alpha=0.3)

# 3. Cumulative distribution
sorted_normalized = np.sort(normalized_labels)
cumulative_norm = np.arange(1, len(sorted_normalized) + 1) / len(sorted_normalized)
axes[1, 2].plot(sorted_normalized, cumulative_norm, color='coral')
axes[1, 2].set_xlabel('Normalized Label Value')
axes[1, 2].set_ylabel('Cumulative Probability')
axes[1, 2].set_title('Normalized Labels - CDF')
axes[1, 2].grid(True, alpha=0.3)

# 4. Statistics text
stats_text_normalized = f"""
Statistics (Normalized):
-----------------------
Total samples: {len(normalized_labels):,}
Mean: {np.mean(normalized_labels):.3f}
Median: {np.median(normalized_labels):.3f}
Std Dev: {np.std(normalized_labels):.3f}
Min: {np.min(normalized_labels):.3f}
Max: {np.max(normalized_labels):.3f}
25th %ile: {np.percentile(normalized_labels, 25):.3f}
75th %ile: {np.percentile(normalized_labels, 75):.3f}
"""
axes[1, 3].text(0.1, 0.5, stats_text_normalized, fontsize=11, family='monospace',
                verticalalignment='center')
axes[1, 3].axis('off')
axes[1, 3].set_title('Normalized Label Statistics')

plt.tight_layout()
plt.savefig('label_distribution_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

print("Visualization saved as 'label_distribution_comparison.png'")
print("\n" + "="*50)
print(stats_text_original)
print("="*50)
print(stats_text_normalized)
print("="*50)