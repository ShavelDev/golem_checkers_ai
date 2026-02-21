import pickle
import numpy as np

with open('training_data.pkl', 'rb') as f:
    training_data = pickle.load(f)

labels = training_data['labels']
normalized_labels = training_data['normalized_labels']
boards = training_data['boards']

# # Convert boards to numpy array of floats

# print(f"Boards shape: {boards.shape}")
# print(f"Boards dtype: {boards.dtype}")
# print(f"Boards min/max: {boards.min()}/{boards.max()}")



boards = np.array(boards, dtype=np.float32)
labels = np.array(labels, dtype=np.float32)
normalized_labels = np.array(normalized_labels, dtype=np.float32)

# # Save back to the pickle file
training_data['boards'] = boards
training_data['labels'] = labels
training_data['normalized_labels'] = normalized_labels
with open('training_data.pkl', 'wb') as f:
    pickle.dump(training_data, f)

print("Training data saved with numpy array boards")