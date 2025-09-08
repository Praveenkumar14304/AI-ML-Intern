import pandas as pd
import numpy as np
import random
from faker import Faker

def generate_synthetic_dataset(rows=10000, filename="synthetic_dataset.csv"):
    fake = Faker()
    data = {}

    # ---------------- Numerical columns (8)
    for i in range(1, 9):
        data[f"num_col_{i}"] = np.random.randint(0, 1000, size=rows) + np.random.randn(rows)*50

    # ---------------- Categorical columns (6)
    cat_options = [
        ['Male', 'Female'],
        ['Yes', 'No'],
        ['Low', 'Medium', 'High'],
        ['Red', 'Green', 'Blue', 'Yellow'],
        ['TypeA', 'TypeB', 'TypeC'],
        ['Group1', 'Group2']
    ]
    for i, opts in enumerate(cat_options, 1):
        data[f"cat_col_{i}"] = np.random.choice(opts, size=rows)

    # ---------------- Text columns (4)
    sample_texts = [
        "Great service and support.",
        "Not satisfied with the product.",
        "Delivery was fast and reliable.",
        "Price is too high for quality.",
        "Customer support resolved my issue.",
        "Loved the experience!",
        "Will not buy again.",
        "Highly recommended.",
        "Average quality, okay for price."
    ]
    for i in range(1, 5):
        data[f"text_col_{i}"] = np.random.choice(sample_texts, size=rows)

    # ---------------- Datetime columns (2)
    start_date = pd.to_datetime("2020-01-01")
    for i in range(1, 3):
        data[f"datetime_col_{i}"] = [start_date + pd.Timedelta(days=random.randint(0, 1000)) for _ in range(rows)]

    # ---------------- Create DataFrame
    df = pd.DataFrame(data)

    # Save CSV
    df.to_csv(filename, index=False)
    print(f"✅ Synthetic dataset saved as {filename}")
    print(f"   Shape: {df.shape}")
    print("   Sample columns:", df.columns.tolist())
    return df

if __name__ == "__main__":
    generate_synthetic_dataset()
