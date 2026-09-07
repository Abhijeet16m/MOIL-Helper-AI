import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import joblib

# --------------------------------
# 1. Load dataset
# --------------------------------

df = pd.read_csv("assets/datasets/training_data_complete.csv")

df = df.drop('REGION_FLAG', axis=1)

# --------------------------------
# 2. Separate 0 and 1 labeled data
# --------------------------------

data_0 = df[df["LABEL"] == 0]
data_1 = df[df["LABEL"] == 1]


# --------------------------------
# 3. Shuffle each class
# --------------------------------

data_0 = data_0.sample(frac=1, random_state=42)
data_1 = data_1.sample(frac=1, random_state=42)


# --------------------------------
# 4. Calculate training sizes
# --------------------------------

train_0_size = int(len(data_0) * 0.80)
train_1_size = int(len(data_1) * 0.90)


# --------------------------------
# 5. Split into training/testing
# --------------------------------

train_0 = data_0.iloc[:train_0_size]
test_0 = data_0.iloc[train_0_size:]

train_1 = data_1.iloc[:train_1_size]
test_1 = data_1.iloc[train_1_size:]


# --------------------------------
# 6. Combine both classes
# --------------------------------

train_data = pd.concat([train_0, train_1])
test_data = pd.concat([test_0, test_1])


# Shuffle training and testing data
train_data = train_data.sample(frac=1, random_state=42)
test_data = test_data.sample(frac=1, random_state=42)


# --------------------------------
# 7. Separate X and Y
# --------------------------------

X_train = train_data.drop("LABEL", axis=1)
y_train = train_data["LABEL"]

X_test = test_data.drop("LABEL", axis=1)
y_test = test_data["LABEL"]


# --------------------------------
# 8. Create XGBClassifier
# --------------------------------

model = XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)

# --------------------------------
# 9. Train the model
# --------------------------------

model.fit(X_train, y_train)


# --------------------------------
# 10. Test the model
# --------------------------------

y_pred = model.predict(X_test)
y_probability = model.predict_proba(X_test)[:, 1]

# --------------------------------
# 11. Calculate accuracy
# --------------------------------

accuracy = accuracy_score(y_test, y_pred)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print("Training 0 labels:", len(train_0))
print("Testing 0 labels:", len(test_0))

print("Training 1 labels:", len(train_1))
print("Testing 1 labels:", len(test_1))

print("Model Accuracy:", accuracy)
print("Model Accuracy (%):", accuracy * 100)

print("\nPredictions:")
for i in range(len(X_test)):
    print(
        f"Actual: {y_test.iloc[i]} | "
        f"Predicted: {y_pred[i]} | "
        f"Mn Probability: {y_probability[i] * 100:.2f}%"
    )

# Saving Model

joblib.dump(model, "Models/XGB_manganese_decision_tree.joblib")

print("Model saved successfully!")