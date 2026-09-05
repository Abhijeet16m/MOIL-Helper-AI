import pandas as pd
import numpy as np
import joblib


# --------------------------------
# 1. Load CSV
# --------------------------------

df = pd.read_csv("training_data_complete.csv")


# --------------------------------
# 2. Load trained model
# --------------------------------

model = joblib.load("manganese_decision_tree.joblib")


# --------------------------------
# 3. Prepare input data
# --------------------------------

X = df.drop("LABEL", axis=1)

actual = df["LABEL"]

# Predict all 212 rows
predicted = model.predict(X)


# --------------------------------
# 4. Create results table
# --------------------------------

results = pd.DataFrame({
    "Row": range(1, len(df) + 1),
    "LAT": df["LATDD"],
    "LON": df["LONDD"],
    "Actual": actual,
    "Predicted": predicted,
    "Correct": actual.to_numpy() == predicted
})


# --------------------------------
# 5. Print table
# --------------------------------

print(results.to_string(index=False))


# --------------------------------
# 6. Overall accuracy
# --------------------------------

accuracy = results["Correct"].mean()

print("\n--------------------------------")
print("Total rows:", len(results))
print("Correct:", results["Correct"].sum())
print("Wrong:", (~results["Correct"]).sum())
print("Accuracy:", accuracy * 100, "%")