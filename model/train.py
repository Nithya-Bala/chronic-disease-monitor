import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
from sklearn.multioutput import MultiOutputClassifier
from imblearn.over_sampling import SMOTE
from skmultilearn.model_selection import iterative_train_test_split
import joblib
import os

# --- Load Dataset ---
df = pd.read_excel(r'C:\Users\sowja\Desktop\sowji\sem 6\ufff\model\Final_dataset.xlsx')

# --- Target Columns ---
target_columns = [
    'Blood_Glucose_Condition',
    'Systolic_BP_Condition',
    'Diastolic_BP_Condition',
    'Temperature_Condition',
    'Heart_Rate_Condition',
    'SPO2_Condition'
]

# --- Encode Target Columns ---
label_encoders = {}
for col in target_columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# --- Drop 'Diabetic/NonDiabetic' and 'Meal Time' from features ---
X = df.drop(columns=target_columns + ['Diabetic/NonDiabetic', 'Meal Time'])
Y = df[target_columns]

# --- Convert to Numpy for Stratified Split ---
X_np = X.values
Y_np = Y.values

X_train_np, Y_train_np, X_test_np, Y_test_np = iterative_train_test_split(X_np, Y_np, test_size=0.2)

X_train = pd.DataFrame(X_train_np, columns=X.columns)
X_test = pd.DataFrame(X_test_np, columns=X.columns)
Y_train = pd.DataFrame(Y_train_np, columns=Y.columns)
Y_test = pd.DataFrame(Y_test_np, columns=Y.columns)

# --- Combine multi-output labels into single label string ---
Y_combined = Y_train.astype(str).agg('_'.join, axis=1)

# --- Remove rare label combinations ---
label_counts = Y_combined.value_counts()
valid_labels = label_counts[label_counts >= 2].index

X_train_filtered = X_train[Y_combined.isin(valid_labels)]
Y_combined_filtered = Y_combined[Y_combined.isin(valid_labels)]

# --- Encode combined labels ---
combined_label_encoder = LabelEncoder()
Y_combined_encoded = combined_label_encoder.fit_transform(Y_combined_filtered)

# --- Apply SMOTE to balance the data ---
smote = SMOTE(k_neighbors=1, random_state=42)
X_resampled, Y_combined_resampled = smote.fit_resample(X_train_filtered, Y_combined_encoded)

# --- Decode back to multi-label format ---
Y_combined_decoded = combined_label_encoder.inverse_transform(Y_combined_resampled)
Y_split = [list(map(int, label.split('_'))) for label in Y_combined_decoded]
Y_train_bal = pd.DataFrame(Y_split, columns=target_columns)
X_train_bal = pd.DataFrame(X_resampled, columns=X.columns)

# --- Scale the features ---
scaler = StandardScaler()
X_train_bal_scaled = pd.DataFrame(scaler.fit_transform(X_train_bal), columns=X.columns)
X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X.columns)

# --- Define Base XGBClassifier ---
xgb_model = XGBClassifier(
    objective='multi:softmax',
    num_class=3,
    eval_metric='mlogloss',
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.5,
    reg_lambda=1.0,
    n_estimators=100,
    random_state=42
)

# --- MultiOutput Classifier ---
multi_output_model = MultiOutputClassifier(xgb_model)

# --- Train the Model ---
multi_output_model.fit(X_train_bal_scaled, Y_train_bal)

# --- Predict on Test Set ---
Y_pred = multi_output_model.predict(X_test_scaled)

# --- Evaluate Model ---
print("\n✅ Model Evaluation on Test Data:")
for i, col in enumerate(target_columns):
    print(f"\n--- {col} ---")
    print(f"Accuracy: {accuracy_score(Y_test[col], Y_pred[:, i]):.4f}")
    print(classification_report(Y_test[col], Y_pred[:, i]))

# --- Save Model and Encoders ---
output_dir = 'model'
os.makedirs(output_dir, exist_ok=True)

joblib.dump(multi_output_model, os.path.join(output_dir, 'multi_output_xgb_model.pkl'))
joblib.dump(label_encoders, os.path.join(output_dir, 'label_encoders.pkl'))
joblib.dump(combined_label_encoder, os.path.join(output_dir, 'combined_label_encoder.pkl'))
joblib.dump(scaler, os.path.join(output_dir, 'scaler.pkl'))

print(f"\n✅ Model and encoders saved successfully in folder: {output_dir}")
print("Before SMOTE:", np.bincount(Y_combined_encoded))
print("After SMOTE:", np.bincount(Y_combined_resampled))

print("\n📌 Input Features used for training:")
print(list(X_train.columns))
