import joblib
import numpy as np

# Load the scaler
scaler = joblib.load("model/scaler.pkl")

# Print the mean of each feature
print("Mean of each feature:", scaler.mean_)

# Print the standard deviation of each feature
print("Standard deviation of each feature:", scaler.scale_)

# Print the number of features
print("Number of features:", scaler.n_features_in_)

# Print the feature names (if available)
print("Feature names:", scaler.feature_names_in_)

# Sample input data (replace with your actual input data)
sample_input = np.array([[
    23, 1, 167.0, 56.0, 20.0796013, 5.6, 257.0, 2345, 5.0,
    1, 1, 1, 1, 1, 99, 40, 96, 123, 67, 90, 0, 0
]])

# Transform the sample input
scaled_input = scaler.transform(sample_input)

# Print the scaled input
print("Scaled input:", scaled_input)
