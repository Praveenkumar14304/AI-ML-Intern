# save as excel_to_ppt_insights.py

import os
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('vader_lexicon')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer

# ==================================================
# 1. Main Orchestrator
# ==================================================
def generate_feature_insights(df, features, target=None, output_json="insights.json", plot_dir="plots"):
    os.makedirs(plot_dir, exist_ok=True)
    results = []

    # Categorize features
    feature_types = categorize_features(df, features)

    # Process each feature
    for f, ftype in feature_types.items():
        results.append(process_feature(df, f, ftype, target, plot_dir))

    # Save JSON
    final_json = {
        "dataset": "Uploaded_Dataset",
        "total_rows": len(df),
        "total_columns": df.shape[1],
        "features": results
    }

    with open(output_json, "w") as f:
        json.dump(final_json, f, indent=4)

    print(f"[INFO] Insights JSON saved at {output_json}")
    return final_json


# ==================================================
# 2. Categorize Features
# ==================================================
def categorize_features(df, features):
    feature_types = {}
    for col in features:
        if pd.api.types.is_numeric_dtype(df[col]):
            feature_types[col] = "Numerical"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            feature_types[col] = "Datetime"
        elif df[col].nunique() < 50:
            feature_types[col] = "Categorical"
        else:
            feature_types[col] = "Text"
    return feature_types


# ==================================================
# 3. Process Feature
# ==================================================
def process_feature(df, feature, ftype, target=None, plot_dir="plots"):
    series = df[feature].dropna()
    if ftype == "Numerical":
        return handle_numerical(df, series, feature, target, plot_dir)
    elif ftype == "Categorical":
        return handle_categorical(df, series, feature, target, plot_dir)
    elif ftype == "Text":
        return handle_text(series, feature, plot_dir)
    elif ftype == "Datetime":
        return handle_datetime(series, feature, plot_dir)


# ==================================================
# 4a. Numerical Features
# ==================================================
def handle_numerical(df, series, feature, target, plot_dir):
    mean, std, skew = series.mean(), series.std(), series.skew()
    q1, q3 = np.percentile(series, [25, 75])
    iqr = q3 - q1
    outlier_percent = (series[(series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)].count() / len(series)) * 100

    if outlier_percent >= 2:
        chosen_plot = "Box plot"
        fig, ax = plt.subplots()
        ax.boxplot(series)
    elif abs(skew) >= 1:
        chosen_plot = "Histogram"
        fig, ax = plt.subplots()
        ax.hist(series, bins=30)
    elif target and target in df:
        chosen_plot = "Scatter"
        fig, ax = plt.subplots()
        ax.scatter(series, df[target])
    else:
        chosen_plot = "KDE"
        fig, ax = plt.subplots()
        series.plot(kind="kde", ax=ax)

    plot_path = save_plot(fig, feature, chosen_plot, plot_dir)

    stats = {"mean": float(mean), "std": float(std), "skew": float(skew), "outlier_percent": float(outlier_percent)}
    insight = f"{feature} has mean {mean:.2f}, skew {skew:.2f}, with {outlier_percent:.1f}% outliers."
    impact = f"The {chosen_plot} highlights distribution aspects of {feature}."

    return build_json_block(feature, "Numerical", chosen_plot, plot_path, stats, insight, impact)


# ==================================================
# 4b. Categorical Features
# ==================================================
def handle_categorical(df, series, feature, target, plot_dir):
    counts = series.value_counts(normalize=True) * 100
    top_cat, top_share = counts.index[0], counts.iloc[0]

    if target and target in df:
        chosen_plot = "Stacked bar"
        fig, ax = plt.subplots()
        pd.crosstab(df[feature], df[target]).plot(kind="bar", stacked=True, ax=ax)
    elif top_share >= 40:
        chosen_plot = "Pareto"
        fig, ax = plt.subplots()
        counts.plot(kind="bar", ax=ax)
    else:
        chosen_plot = "Frequency bar"
        fig, ax = plt.subplots()
        counts.head(10).plot(kind="bar", ax=ax)

    plot_path = save_plot(fig, feature, chosen_plot, plot_dir)

    stats = {"unique_values": int(series.nunique()), "top_categories": counts.to_dict()}
    insight = f"{feature} is dominated by '{top_cat}' with {top_share:.1f}% share."
    impact = f"The {chosen_plot} shows distribution across categories."

    return build_json_block(feature, "Categorical", chosen_plot, plot_path, stats, insight, impact)


# ==================================================
# 4c. Text Features
# ==================================================
def handle_text(series, feature, plot_dir):
    lengths = series.astype(str).apply(lambda x: len(x.split()))
    median_len = lengths.median()

    # TF-IDF bigrams
    vectorizer = TfidfVectorizer(ngram_range=(2, 2), max_features=5)
    try:
        vectorizer.fit(series.astype(str))
        bigrams = vectorizer.get_feature_names_out()
    except:
        bigrams = []

    # Sentiment
    sentiment_scores = series.astype(str).apply(lambda x: TextBlob(x).sentiment.polarity)

    chosen_plot = "Length histogram"
    fig, ax = plt.subplots()
    ax.hist(lengths, bins=30)
    plot_path = save_plot(fig, feature, chosen_plot, plot_dir)

    stats = {"median_length": float(median_len), "top_bigrams": list(bigrams), "sentiment_std": float(sentiment_scores.std())}
    insight = f"{feature} comments have median length {median_len:.1f} words. Common bigrams: {', '.join(bigrams)}."
    impact = f"The {chosen_plot} highlights text complexity and themes."

    return build_json_block(feature, "Text", chosen_plot, plot_path, stats, insight, impact)


# ==================================================
# 4d. Datetime Features
# ==================================================
def handle_datetime(series, feature, plot_dir):
    daily_counts = series.dt.to_period("D").value_counts().sort_index()

    chosen_plot = "Time trend"
    fig, ax = plt.subplots()
    daily_counts.plot(ax=ax)
    plot_path = save_plot(fig, feature, chosen_plot, plot_dir)

    stats = {"start_date": str(series.min()), "end_date": str(series.max()), "peak_day": str(daily_counts.idxmax())}
    insight = f"{feature} shows peak activity on {stats['peak_day']}."
    impact = f"The {chosen_plot} highlights seasonality and trends."

    return build_json_block(feature, "Datetime", chosen_plot, plot_path, stats, insight, impact)


# ==================================================
# Helpers
# ==================================================
def save_plot(fig, feature, plot_type, folder):
    file_path = os.path.join(folder, f"{feature}_{plot_type.replace(' ', '').lower()}.png")
    fig.savefig(file_path, bbox_inches="tight")
    plt.close(fig)
    return file_path


def build_json_block(feature, ftype, chosen_plot, plot_path, stats, insight, impact):
    return {
        "feature": feature,
        "type": ftype,
        "chosen_plot": chosen_plot,
        "plot_path": plot_path,
        "statistics": stats,
        "insight_suggestion": insight,
        "insight_impact": impact
    }


# ==================================================
# 5. CSV Loader and Main Function
# ==================================================
def analyze_csv_file(csv_file_path, target_column=None, output_json="insights.json", plot_dir="plots"):
    """
    Main function to load a CSV file and generate insights
    
    Parameters:
    csv_file_path (str): Path to the CSV file
    target_column (str, optional): Target column for analysis
    output_json (str): Output JSON file name
    plot_dir (str): Directory to save plots
    
    Returns:
    dict: Insights in JSON format
    """
    try:
        # Load the CSV file
        df = pd.read_csv(csv_file_path)
        print(f"[INFO] Successfully loaded data with {df.shape[0]} rows and {df.shape[1]} columns")
        
        # Display column information
        print("\n[INFO] Column Information:")
        for i, col in enumerate(df.columns, 1):
            col_type = "Numerical" if pd.api.types.is_numeric_dtype(df[col]) else \
                      "Datetime" if pd.api.types.is_datetime64_any_dtype(df[col]) else \
                      "Categorical" if df[col].nunique() < 50 else "Text"
            print(f"  {i}. {col} ({col_type})")
        
        # Extract feature columns (all columns except target if specified)
        if target_column and target_column in df.columns:
            features = [col for col in df.columns if col != target_column]
            print(f"\n[INFO] Analyzing {len(ffeatures)} features with '{target_column}' as target")
        else:
            features = list(df.columns)
            if target_column and target_column not in df.columns:
                print(f"[WARNING] Target column '{target_column}' not found in dataset. Proceeding without target analysis.")
            print(f"\n[INFO] Analyzing all {len(features)} features")
        
        # Generate insights
        insights = generate_feature_insights(df, features, target_column, output_json, plot_dir)
        
        # Print insights in JSON format
        print("\n" + "="*50)
        print("ANALYSIS INSIGHTS SUMMARY")
        print("="*50)
        print(json.dumps(insights, indent=4))
        
        return insights
        
    except Exception as e:
        print(f"[ERROR] Failed to analyze CSV file: {str(e)}")
        return None


# ==================================================
# 6. Run Example with Default CSV File
# ==================================================
if __name__ == "__main__":
    # Default CSV file path for testing
    DEFAULT_CSV_FILE = "synthetic_dataset.csv"
    
    # Create sample CSV file for testing if it doesn't exist
    if not os.path.exists(DEFAULT_CSV_FILE):
        print(f"[INFO] Creating sample CSV file: {DEFAULT_CSV_FILE}")
        sample_data = {
            "Age": [22, 25, 30, 45, 35, 100, 29, 32, 41, 28],
            "Gender": ["Male", "Female", "Male", "Female", "Female", "Male", "Male", "Female", "Male", "Female"],
            "Feedback": [
                "Great service", 
                "Bad product", 
                "Customer support was helpful", 
                "Too expensive", 
                "Loved it", 
                "Terrible quality", 
                "Fast delivery",
                "Average experience",
                "Would recommend to others",
                "Poor customer service"
            ],
            "Signup_Date": pd.date_range("2021-01-01", periods=10, freq="D"),
            "Score": [85, 45, 90, 30, 95, 20, 88, 60, 92, 35]
        }
        
        # Create sample CSV
        sample_df = pd.DataFrame(sample_data)
        sample_df.to_csv(DEFAULT_CSV_FILE, index=False)
    
    # Analyze the CSV file with default target column
    print(f"[INFO] Analyzing CSV file: {DEFAULT_CSV_FILE}")
    insights = analyze_csv_file(DEFAULT_CSV_FILE, "Score")
    
    if insights:
        print(f"\n[SUCCESS] Analysis complete! Results saved to insights.json")
        print(f"Plots saved to directory: plots")