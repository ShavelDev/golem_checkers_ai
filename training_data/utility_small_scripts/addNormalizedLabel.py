import pickle
import numpy as np

# Load training data
with open('training_data.pkl', 'rb') as f:
    training_data = pickle.load(f)

labels = training_data['labels']

# Normalize labels using tanh
# You can adjust the divisor to control the spread
# Smaller divisor = more aggressive normalization (values closer to -1 and 1)
# Larger divisor = gentler normalization (values closer to 0)
divisor = 30.0  # Adjust this based on your label distribution

normalized_labels = [np.tanh(label / divisor) for label in labels]

# Add normalized labels to the dictionary
training_data['normalized_labels'] = normalized_labels

# Save back to file
with open('training_data.pkl', 'wb') as f:
    pickle.dump(training_data, f)

# Print statistics
print(f"Original labels:")
print(f"  Min: {np.min(labels):.3f}, Max: {np.max(labels):.3f}")
print(f"  Mean: {np.mean(labels):.3f}, Std: {np.std(labels):.3f}")
print()
print(f"Normalized labels (tanh with divisor={divisor}):")
print(f"  Min: {np.min(normalized_labels):.3f}, Max: {np.max(normalized_labels):.3f}")
print(f"  Mean: {np.mean(normalized_labels):.3f}, Std: {np.std(normalized_labels):.3f}")
print()
print(f"Added 'normalized_labels' field to training_data.pkl")