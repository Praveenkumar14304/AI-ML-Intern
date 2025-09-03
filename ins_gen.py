import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from scipy.stats import entropy

# ========== 1. Load Dataset ==========
df = pd.read_csv("customer_churn_dataset.csv")

# Ensure output folders exist
os.makedirs("plots", exist_ok=True)
os.makedirs("feature_json", exist_ok=True)

# ========== 2. Feature Type Detection ==========
num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
datetime_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64']).columns.tolist()

# Handle low-cardinality numeric columns as categorical
for col in num_cols.copy():
    if df[col].nunique() < 20:
        cat_cols.append(col)
        num_cols.remove(col)

print("Numerical Columns:", num_cols)
print("Categorical Columns:", cat_cols)
print("Datetime Columns:", datetime_cols)


# ========== 3. Processing Functions ==========
def process_numerical(df, col):
    s = df[col].dropna()

    stats = {
        "column_name": col,
        "mean": float(s.mean()),
        "median": float(s.median()),
        "mode": float(s.mode().iloc[0]) if not s.mode().empty else None,
        "std": float(s.std()),
        "min": float(s.min()),
        "max": float(s.max()),
        "skewness": float(s.skew()),
        "kurtosis": float(s.kurt()),
        "missing_values": int(df[col].isna().sum()),
        "unique_values": int(s.nunique())
    }

    # Conditional Plot
    plot_path = f"plots/{col}.png"
    plt.figure(figsize=(6, 4))

    if stats["unique_values"] > 20 and abs(stats["skewness"]) < 2:
        # Continuous → Histogram
        sns.histplot(s, kde=True, bins=30)
        plt.title(f"Histogram of {col}")
    elif stats["unique_values"] > 20 and abs(stats["skewness"]) >= 2:
        # Highly skewed → Boxplot
        sns.boxplot(x=s)
        plt.title(f"Boxplot of {col} (Skewed)")
    else:
        # Low cardinality numeric → Bar
        s.value_counts().plot(kind="bar")
        plt.title(f"Bar Chart of {col}")

    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    stats["plot_path"] = plot_path
    return stats


def process_categorical(df, col):
    s = df[col].dropna()
    value_counts = s.value_counts(dropna=False)
    percentages = value_counts / value_counts.sum() * 100

    stats = {
        "column_name": col,
        "unique_values": int(s.nunique(dropna=False)),
        "most_frequent": str(value_counts.idxmax()) if not value_counts.empty else None,
        "most_frequent_count": int(value_counts.max()) if not value_counts.empty else None,
        "least_frequent": str(value_counts.idxmin()) if not value_counts.empty else None,
        "least_frequent_count": int(value_counts.min()) if not value_counts.empty else None,
        "missing_values": int(df[col].isna().sum()),
        "entropy": float(entropy(value_counts)) if not value_counts.empty else None
    }

    # Conditional Plot
    plot_path = f"plots/{col}.png"
    plt.figure(figsize=(6, 4))

    if stats["unique_values"] <= 5 and percentages.max() < 80:
        # Few categories + balanced → Pie chart
        value_counts.plot(kind="pie", autopct="%1.1f%%")
        plt.ylabel("")
        plt.title(f"Pie Chart of {col}")
    else:
        # Many or imbalanced → Bar chart
        value_counts.head(10).plot(kind="bar")
        plt.title(f"Bar Chart of {col} (Top 10)")
        plt.ylabel("Count")

    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    stats["plot_path"] = plot_path
    return stats


def process_datetime(df, col):
    df[col] = pd.to_datetime(df[col], errors="coerce")
    series = df[col].dropna().sort_values()

    stats = {"column_name": col, "missing_values": int(df[col].isna().sum())}

    if series.empty:
        stats.update({"error": "No valid dates"})
        return stats

    gaps = series.diff().dropna().dt.days

    stats.update({
        "min_date": str(series.min().date()),
        "max_date": str(series.max().date()),
        "time_span_days": int((series.max() - series.min()).days),
        "most_frequent_date": str(series.value_counts().idxmax().date()),
        "repeated_dates": int((series.value_counts() > 1).sum()),
        "avg_gap_days": float(gaps.mean()) if not gaps.empty else None,
        "median_gap_days": float(gaps.median()) if not gaps.empty else None,
    })

    # Conditional Plot
    plot_path = f"plots/{col}.png"
    plt.figure(figsize=(8, 4))

    if stats["time_span_days"] > 365:
        # Long span → yearly trend
        series.groupby(series.dt.to_period("Y")).count().plot()
        plt.title(f"Yearly Trend of {col}")
    else:
        # Short span → daily trend
        series.value_counts().sort_index().plot()
        plt.title(f"Daily Trend of {col}")

    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    stats["plot_path"] = plot_path
    return stats


# ========== 4. Main Function ==========
def generate_insights(df, num_cols, cat_cols, datetime_cols, print_stats=False, save_json=True, save_dir="feature_json"):
    insights = {"numerical": {}, "categorical": {}, "datetime": {}}

    # Numerical
    for col in num_cols:
        insights["numerical"][col] = process_numerical(df, col)
        if print_stats:
            print(json.dumps(insights["numerical"][col], indent=4))

    # Categorical
    for col in cat_cols:
        insights["categorical"][col] = process_categorical(df, col)
        if print_stats:
            print(json.dumps(insights["categorical"][col], indent=4))

    # Datetime
    for col in datetime_cols:
        insights["datetime"][col] = process_datetime(df, col)
        if print_stats:
            print(json.dumps(insights["datetime"][col], indent=4))

    # Save JSONs separately (only if not empty)
    if save_json:
        os.makedirs(save_dir, exist_ok=True)

        if insights["numerical"]:
            with open(os.path.join(save_dir, "numerical_insights.json"), "w") as f:
                json.dump(insights["numerical"], f, indent=4)

        if insights["categorical"]:
            with open(os.path.join(save_dir, "categorical_insights.json"), "w") as f:
                json.dump(insights["categorical"], f, indent=4)

        if insights["datetime"]:
            with open(os.path.join(save_dir, "datetime_insights.json"), "w") as f:
                json.dump(insights["datetime"], f, indent=4)

    return insights


# ========== 5. Example Run ==========
if __name__ == "__main__":
    all_insights = generate_insights(df, num_cols, cat_cols, datetime_cols, print_stats=False, save_json=False)
    print("\n✅ Conditional plots + JSONs created.")
