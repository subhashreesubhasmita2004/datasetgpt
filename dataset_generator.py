import pandas as pd
import numpy as np
import random

def generate_dataset(
    rows,
    columns,
    missing_rate=0,
    add_duplicates=False,
    add_outliers=False,
    add_inconsistent=False,
    add_noise=False,
    imbalance_column=None
):

    data = {}


    for col in columns:
        col = col.strip().lower()

        if "name" in col:
            data[col] = ["Name_" + str(i) for i in range(rows)]

        elif "patient_id" in col or "id" in col:
            data[col] = list(range(1, rows+1))

        elif "email" in col:
            data[col] = [f"user{i}@gmail.com" for i in range(rows)]

        elif "age" in col:
            data[col] = np.random.randint(1, 90, rows)

        elif "gender" in col:
            data[col] = np.random.choice(["Male", "Female"], rows)

        elif "diagnosis" in col:
            data[col] = np.random.choice(
                ["Diabetes", "Hypertension", "Heart Disease", "Healthy"],
                rows
            )

        elif "city" in col:
            data[col] = np.random.choice(
                ["Bhubaneswar", "Delhi", "Mumbai", "Hyderabad"],
                rows
            )

        elif "blood_pressure" in col:
            data[col] = np.random.randint(80, 180, rows)

        elif "sugar" in col:
            data[col] = np.random.randint(70, 200, rows)

        elif "treatment_cost" in col:
            data[col] = np.random.randint(5000, 50000, rows)

        elif "recovery_days" in col:
            data[col] = np.random.randint(1, 30, rows)

        elif "probability" in col:
            data[col] = np.round(np.random.rand(rows), 2)

        else:
            data[col] = np.random.randint(1, 100, rows)

    df = pd.DataFrame(data)
    
    
    if "patient_id" in df.columns:
        df["patient_id"] = range(1, len(df)+1)

    if missing_rate > 0:
        for col in df.columns:
            if "id" not in col.lower():   # protect ID column
                mask = np.random.random(len(df)) < missing_rate
                df.loc[mask, col] = np.nan

    if add_duplicates:
        dup_df = df.sample(frac=0.1).copy()
        
        if "patient_id" in dup_df.columns:
            dup_df["patient_id"] = range(len(df)+1, len(df)+1+len(dup_df))
        
        df = pd.concat([df, dup_df], ignore_index=True)

    if add_outliers:
        for col in df.select_dtypes(include=np.number).columns:
            if "id" in col.lower():  # skip patient_id or any ID column
                continue
            idx = np.random.choice(df.index, size=int(0.05 * len(df)))
            df.loc[idx, col] = df[col] * 10

    if add_inconsistent:
        for col in df.columns:
            if "id" in col.lower():  
                continue
            idx = np.random.choice(df.index, size=int(0.05 * len(df)))
            df[col] = df[col].astype(object)   
            df.loc[idx, col] = "INVALID"

    if add_noise:
        df["random_noise"] = np.random.randn(len(df))

    if imbalance_column and imbalance_column in df.columns:
        if "diagnosis" in imbalance_column.lower():
            df[imbalance_column] = np.random.choice(
                ["Diabetes", "Healthy"],
                size=len(df),
                p=[0.9, 0.1]
            )
        else:
            df[imbalance_column] = np.random.choice([0,1], size=len(df), p=[0.9,0.1])
    
    priority_cols = ["patient_id", "name"]

    priority_cols = [col for col in priority_cols if col in df.columns]

    other_cols = [col for col in df.columns if col not in priority_cols]

    df = df[priority_cols + other_cols]
    return df  