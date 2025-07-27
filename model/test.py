import joblib
model = joblib.load("model/multi_output_xgb_model.pkl")
test_input = [[120, 80, 70, 75, 36.5, 98]]
try:
    output = model.predict(test_input)
    print(output)
except ValueError as e:
    print("Error:", e)
