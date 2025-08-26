import pandas as pd

# --- Step 1: Read the data ---
# Separator is '/'
df = pd.read_csv(r"imine.dtm", sep="/", header=None, names=["Name", "PedalVolume", "Photoisomerizable"])

# --- Step 2: Convert numeric columns ---
df["PedalVolume"] = pd.to_numeric(df["PedalVolume"], errors="coerce")
df["Photoisomerizable"] = pd.to_numeric(df["Photoisomerizable"], errors="coerce")

# Drop rows with missing values
df = df.dropna(subset=["PedalVolume", "Photoisomerizable"]).reset_index(drop=True)
df["Photoisomerizable"] = df["Photoisomerizable"].astype(int)

# --- Step 3: Sort by PedalVolume ---
df_sorted = df.sort_values(by="PedalVolume").reset_index(drop=True)

# --- Step 4: Find best threshold ---
best_threshold = None
best_error = len(df_sorted)

for i in range(len(df_sorted) - 1):
    # Midpoint between current and next value
    threshold = (df_sorted.loc[i, "PedalVolume"] + df_sorted.loc[i+1, "PedalVolume"]) / 2
    # Predict using threshold
    preds = (df_sorted["PedalVolume"] >= threshold).astype(int)
    # Count errors
    errors = (preds != df_sorted["Photoisomerizable"]).sum()
    if errors < best_error:
        best_error = errors
        best_threshold = threshold

# --- Step 5: Compute accuracy ---
preds_best = (df_sorted["PedalVolume"] >= best_threshold).astype(int)
accuracy = (preds_best == df_sorted["Photoisomerizable"]).mean()

# --- Step 6: Output ---
print("Best Threshold:", best_threshold)
print("Misclassifications:", best_error)
print("Accuracy:", accuracy)
