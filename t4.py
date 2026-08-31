import joblib
import pandas as pd
from test import get_all_environmental_data

lat, lon = (-13.9758582,136.4227798)

model = joblib.load("manganese_decision_tree.joblib")

START_DATE = "2025-08-01"
END_DATE = "2026-08-01"
YEAR = 2025
fetched = get_all_environmental_data(lat, lon,start_date=START_DATE, end_date=END_DATE, year=YEAR)

data = {}
data["LATDD"] = lat
data["LONDD"] = lon
data["REGION_FLAG"] = 2
data["BIOME_ID"] = 9
data["LABEL"] = 1

data.update(fetched)

df = pd.DataFrame([data])
print(df)

X = df.drop("LABEL", axis=1)

actual = df["LABEL"]

# Predict all 212 rows
predicted = model.predict(X)

print(f"Predicted: {predicted}\nActual: {actual}")