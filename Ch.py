import json
import os
import random
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import nltk
from collections import Counter
import re

class HotelBookingVisualization:
    def __init__(self, dataset_path="hotel_booking.csv"):
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
            '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5'
        ]
        self.used_colors = set()
        self.output_dir = "output"
        self.dataset_path = dataset_path
        self.dataset = None
        self.setup_directories()
        self.load_dataset()
        
    def setup_directories(self):
        """Create necessary output directories"""
        os.makedirs(os.path.join(self.output_dir, "charts"), exist_ok=True)
    
    def load_dataset(self):
        """Load the hotel booking dataset"""
        if os.path.exists(self.dataset_path):
            self.dataset = pd.read_csv(self.dataset_path)
            print(f"Loaded dataset: {self.dataset_path}")
            print(f"Dataset shape: {self.dataset.shape}")
        else:
            print(f"Error: Dataset not found at {self.dataset_path}")
    
    def get_unique_color(self):
        """Get a unique color from the palette that hasn't been used yet"""
        available_colors = [c for c in self.color_palette if c not in self.used_colors]
        
        if not available_colors:
            self.used_colors = set()
            available_colors = self.color_palette.copy()
        
        color = random.choice(available_colors)
        self.used_colors.add(color)
        return color
    
    def find_best_column_match(self, metric_name):
        """Find the best matching column using fuzzy matching"""
        metric_lower = metric_name.lower()
        
        if metric_lower in [col.lower() for col in self.dataset.columns]:
            for col in self.dataset.columns:
                if col.lower() == metric_lower:
                    return col
        
        for col in self.dataset.columns:
            col_lower = col.lower()
            if metric_lower in col_lower or col_lower in metric_lower:
                return col
        
        words = metric_lower.split('_')
        for col in self.dataset.columns:
            col_lower = col.lower()
            if any(word in col_lower for word in words if len(word) > 3):
                return col
        
        return self.dataset.columns[0] if len(self.dataset.columns) > 0 else None
    
    def is_numeric_column(self, series):
        """Check if a pandas series contains numeric data"""
        try:
            pd.to_numeric(series)
            return True
        except (ValueError, TypeError):
            return False
    
    def is_date_column(self, series):
        """Check if a pandas series contains date data"""
        sample_size = min(10, len(series))
        if sample_size == 0:
            return False
        
        sample = series.dropna().head(sample_size)
        date_patterns = [r'\d{4}-\d{2}-\d{2}', r'\d{2}/\d{2}/\d{4}', r'\d{4}/\d{2}/\d{2}']
        
        for value in sample:
            if isinstance(value, str) and any(re.match(pattern, value) for pattern in date_patterns):
                return True
            if isinstance(value, (datetime, pd.Timestamp)):
                return True
        return False
    
    def generate_numerical_insights(self, data, column_name):
        """Generate insights for numerical columns"""
        numeric_data = pd.to_numeric(data[column_name], errors='coerce').dropna()
        
        if len(numeric_data) == 0:
            return {"error": "No valid numerical data found"}
        
        insights = {
            "data_type": "numerical",
            "basic_statistics": {
                "mean": float(numeric_data.mean()),
                "median": float(numeric_data.median()),
                "std_dev": float(numeric_data.std()),
                "min": float(numeric_data.min()),
                "max": float(numeric_data.max()),
                "range": float(numeric_data.max() - numeric_data.min())
            },
            "quartiles": {
                "q1": float(numeric_data.quantile(0.25)),
                "q3": float(numeric_data.quantile(0.75)),
                "iqr": float(numeric_data.quantile(0.75) - numeric_data.quantile(0.25))
            },
            "distribution": {
                "skewness": float(numeric_data.skew()),
                "total_values": int(len(numeric_data)),
                "zero_values": int((numeric_data == 0).sum())
            }
        }
        
        # Outlier analysis
        Q1 = numeric_data.quantile(0.25)
        Q3 = numeric_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = numeric_data[(numeric_data < lower_bound) | (numeric_data > upper_bound)]
        
        insights["outlier_analysis"] = {
            "outlier_count": int(len(outliers)),
            "outlier_percentage": float(len(outliers) / len(numeric_data) * 100),
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound)
        }
        
        # Value ranges
        insights["value_ranges"] = {
            "low_range": f"< {Q1:.2f}",
            "medium_range": f"{Q1:.2f} - {Q3:.2f}",
            "high_range": f"> {Q3:.2f}"
        }
        
        return insights
    
    def generate_categorical_insights(self, data, column_name):
        """Generate insights for categorical columns"""
        categorical_data = data[column_name].astype(str)
        value_counts = categorical_data.value_counts()
        total_count = len(categorical_data.dropna())
        
        insights = {
            "data_type": "categorical",
            "basic_statistics": {
                "unique_categories": int(len(value_counts)),
                "total_values": int(total_count),
                "most_frequent_value": str(value_counts.index[0]) if len(value_counts) > 0 else "N/A",
                "most_frequent_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
            },
            "category_distribution": {}
        }
        
        # Top categories
        top_categories = value_counts.head(10)
        for category, count in top_categories.items():
            percentage = (count / total_count) * 100
            insights["category_distribution"][str(category)] = {
                "count": int(count),
                "percentage": float(percentage)
            }
        
        # Diversity analysis
        if len(value_counts) > 0:
            insights["diversity_analysis"] = {
                "dominance_percentage": float((value_counts.iloc[0] / total_count) * 100),
                "top_5_concentration": float((value_counts.head(5).sum() / total_count) * 100),
                "entropy": float(-sum((count/total_count) * np.log2(count/total_count) 
                                   for count in value_counts if count > 0))
            }
        
        return insights
    
    def generate_text_insights(self, data, column_name):
        """Generate insights for text columns using basic NLP"""
        text_data = data[column_name].astype(str)
        all_text = ' '.join(text_data)
        
        # Basic text statistics
        words = re.findall(r'\b\w+\b', all_text.lower())
        word_counts = Counter(words)
        
        insights = {
            "data_type": "text",
            "basic_statistics": {
                "total_records": int(len(text_data)),
                "total_words": int(len(words)),
                "unique_words": int(len(word_counts)),
                "average_words_per_record": float(len(words) / len(text_data))
            },
            "most_common_words": {},
            "text_patterns": {}
        }
        
        # Most common words (excluding stop words)
        common_words = word_counts.most_common(20)
        for word, count in common_words:
            if len(word) > 2:  # Filter out short words
                insights["most_common_words"][word] = {
                    "count": int(count),
                    "percentage": float((count / len(words)) * 100)
                }
        
        # Text length analysis
        text_lengths = text_data.str.len()
        insights["text_patterns"]["length_analysis"] = {
            "average_length": float(text_lengths.mean()),
            "max_length": int(text_lengths.max()),
            "min_length": int(text_lengths.min())
        }
        
        return insights
    
    def generate_date_insights(self, data, column_name):
        """Generate insights for date columns"""
        try:
            date_data = pd.to_datetime(data[column_name], errors='coerce').dropna()
            
            if len(date_data) == 0:
                return {"error": "No valid date data found"}
            
            insights = {
                "data_type": "date",
                "basic_statistics": {
                    "date_range": {
                        "earliest_date": date_data.min().strftime("%Y-%m-%d"),
                        "latest_date": date_data.max().strftime("%Y-%m-%d"),
                        "total_days": int((date_data.max() - date_data.min()).days)
                    },
                    "total_records": int(len(date_data))
                },
                "temporal_patterns": {}
            }
            
            # Monthly patterns
            monthly_counts = date_data.dt.month.value_counts().sort_index()
            insights["temporal_patterns"]["monthly_distribution"] = {
                str(i): int(monthly_counts.get(i, 0)) for i in range(1, 13)
            }
            
            # Day of week patterns
            weekday_counts = date_data.dt.dayofweek.value_counts().sort_index()
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            insights["temporal_patterns"]["weekday_distribution"] = {
                days[i]: int(weekday_counts.get(i, 0)) for i in range(7)
            }
            
            return insights
            
        except Exception as e:
            return {"error": f"Error processing date data: {str(e)}"}
    
    def generate_insights(self, data, column_name, metric_name):
        """Generate comprehensive insights based on data type"""
        if data is None or column_name not in data.columns:
            return {"error": f"Column {column_name} not found in dataset"}
        
        # Determine data type
        if self.is_date_column(data[column_name]):
            return self.generate_date_insights(data, column_name)
        elif self.is_numeric_column(data[column_name]):
            return self.generate_numerical_insights(data, column_name)
        elif data[column_name].dtype == 'object' and data[column_name].str.len().mean() > 50:
            return self.generate_text_insights(data, column_name)
        else:
            return self.generate_categorical_insights(data, column_name)
    
    def create_chart(self, data, column_name, metric_name, chart_type):
        """Create a chart using Plotly based on the chart type"""
        color = self.get_unique_color()
        fig = None
        
        try:
            if chart_type == "line":
                if self.is_numeric_column(data[column_name]):
                    numeric_data = pd.to_numeric(data[column_name], errors='coerce').dropna()
                    fig = px.line(y=numeric_data.values, title=f"{metric_name} Trend")
                    fig.update_traces(line=dict(color=color))
                    
            elif chart_type == "bar":
                if self.is_numeric_column(data[column_name]):
                    numeric_data = pd.to_numeric(data[column_name], errors='coerce').dropna()
                    fig = px.bar(y=numeric_data.values, title=f"{metric_name} Distribution")
                    fig.update_traces(marker_color=color)
                else:
                    value_counts = data[column_name].value_counts().head(10)
                    fig = px.bar(x=value_counts.index, y=value_counts.values, 
                               title=f"{metric_name} Distribution")
                    fig.update_traces(marker_color=color)
                    
            elif chart_type == "pie":
                value_counts = data[column_name].value_counts().head(10)
                fig = px.pie(values=value_counts.values, names=value_counts.index,
                           title=f"{metric_name} Distribution")
                
            elif chart_type == "scatter":
                if self.is_numeric_column(data[column_name]):
                    numeric_data = pd.to_numeric(data[column_name], errors='coerce').dropna()
                    fig = px.scatter(y=numeric_data.values, title=f"{metric_name} Scatter Plot")
                    fig.update_traces(marker=dict(color=color))
                    
            elif chart_type == "histogram":
                if self.is_numeric_column(data[column_name]):
                    numeric_data = pd.to_numeric(data[column_name], errors='coerce').dropna()
                    fig = px.histogram(x=numeric_data.values, title=f"{metric_name} Histogram")
                    fig.update_traces(marker_color=color)
            
            if fig:
                fig.update_layout(
                    width=800,
                    height=500,
                    showlegend=False
                )
                
        except Exception as e:
            print(f"Error creating chart for {metric_name}: {e}")
            fig = go.Figure()
            fig.add_annotation(text=f"Chart not available: {e}", x=0.5, y=0.5, showarrow=False)
        
        return fig, color
    
    def process_insights(self, insights_config):
        """Process insights-only configuration"""
        results = []
        
        for metric_name in insights_config:
            column_name = self.find_best_column_match(metric_name)
            if not column_name:
                continue
                
            insights = self.generate_insights(self.dataset, column_name, metric_name)
            
            results.append({
                "metric_name": metric_name,
                "column_used": column_name,
                "insights": insights
            })
        
        # Save to single JSON file
        output_path = os.path.join(self.output_dir, "insights.json")
        with open(output_path, 'w') as f:
            json.dump({"analysis_type": "insights", "results": results}, f, indent=2)
        
        return results
    
    def process_insights_charts(self, insights_charts_config):
        """Process insights with charts configuration"""
        results = []
        
        for metric_name, chart_type in insights_charts_config.items():
            column_name = self.find_best_column_match(metric_name)
            if not column_name:
                continue
                
            insights = self.generate_insights(self.dataset, column_name, metric_name)
            fig, chart_color = self.create_chart(self.dataset, column_name, metric_name, chart_type)
            
            # Save chart
            chart_filename = f"{metric_name}_{chart_type}.png"
            chart_path = os.path.join(self.output_dir, "charts", chart_filename)
            fig.write_image(chart_path)
            
            results.append({
                "metric_name": metric_name,
                "column_used": column_name,
                "chart_type": chart_type,
                "chart_color": chart_color,
                "chart_path": chart_path,
                "insights": insights
            })
        
        # Save to single JSON file
        output_path = os.path.join(self.output_dir, "insights_charts.json")
        with open(output_path, 'w') as f:
            json.dump({"analysis_type": "insights_charts", "results": results}, f, indent=2)
        
        return results
    
    def process_comparison(self, comparison_config):
        """Process comparison configuration"""
        results = []
        
        for comparison_name, chart_type in comparison_config.items():
            # Extract column names from comparison name
            columns = comparison_name.split('_vs_')
            if len(columns) != 2:
                continue
                
            col1_name = self.find_best_column_match(columns[0])
            col2_name = self.find_best_column_match(columns[1])
            
            if not col1_name or not col2_name:
                continue
            
            # Generate comparison insights
            col1_insights = self.generate_insights(self.dataset, col1_name, columns[0])
            col2_insights = self.generate_insights(self.dataset, col2_name, columns[1])
            
            # Create comparison chart
            color = self.get_unique_color()
            fig = self.create_comparison_chart(self.dataset, col1_name, col2_name, chart_type, color)
            
            # Save chart
            chart_filename = f"{comparison_name}_{chart_type}.png"
            chart_path = os.path.join(self.output_dir, "charts", chart_filename)
            fig.write_image(chart_path)
            
            # Generate comparison insights
            comparison_insights = self.generate_comparison_insights(
                self.dataset, col1_name, col2_name, columns[0], columns[1]
            )
            
            results.append({
                "comparison_name": comparison_name,
                "columns_compared": [col1_name, col2_name],
                "chart_type": chart_type,
                "chart_color": color,
                "chart_path": chart_path,
                "individual_insights": {
                    columns[0]: col1_insights,
                    columns[1]: col2_insights
                },
                "comparison_insights": comparison_insights
            })
        
        # Save to single JSON file
        output_path = os.path.join(self.output_dir, "comparison.json")
        with open(output_path, 'w') as f:
            json.dump({"analysis_type": "comparison", "results": results}, f, indent=2)
        
        return results
    
    def create_comparison_chart(self, data, col1_name, col2_name, chart_type, color):
        """Create comparison chart between two columns"""
        fig = None
        
        try:
            if chart_type == "scatter":
                if (self.is_numeric_column(data[col1_name]) and 
                    self.is_numeric_column(data[col2_name])):
                    
                    col1_data = pd.to_numeric(data[col1_name], errors='coerce').dropna()
                    col2_data = pd.to_numeric(data[col2_name], errors='coerce').dropna()
                    
                    # Ensure same length
                    min_len = min(len(col1_data), len(col2_data))
                    fig = px.scatter(x=col1_data.head(min_len), y=col2_data.head(min_len),
                                   title=f"{col1_name} vs {col2_name}")
                    fig.update_traces(marker=dict(color=color))
                    
            elif chart_type == "line":
                if (self.is_numeric_column(data[col1_name]) and 
                    self.is_numeric_column(data[col2_name])):
                    
                    col1_data = pd.to_numeric(data[col1_name], errors='coerce').dropna()
                    col2_data = pd.to_numeric(data[col2_name], errors='coerce').dropna()
                    
                    min_len = min(len(col1_data), len(col2_data))
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=col1_data.head(min_len), 
                                           y=col2_data.head(min_len),
                                           mode='lines', line=dict(color=color)))
                    fig.update_layout(title=f"{col1_name} vs {col2_name}")
                    
        except Exception as e:
            print(f"Error creating comparison chart: {e}")
            fig = go.Figure()
            fig.add_annotation(text=f"Chart not available: {e}", x=0.5, y=0.5, showarrow=False)
        
        if fig:
            fig.update_layout(width=800, height=500)
        return fig
    
    def generate_comparison_insights(self, data, col1_name, col2_name, metric1, metric2):
        """Generate insights comparing two columns"""
        insights = {}
        
        try:
            if (self.is_numeric_column(data[col1_name]) and 
                self.is_numeric_column(data[col2_name])):
                
                col1_data = pd.to_numeric(data[col1_name], errors='coerce').dropna()
                col2_data = pd.to_numeric(data[col2_name], errors='coerce').dropna()
                
                # Correlation analysis
                min_len = min(len(col1_data), len(col2_data))
                if min_len > 1:
                    correlation = np.corrcoef(col1_data.head(min_len), col2_data.head(min_len))[0,1]
                    insights["correlation_analysis"] = {
                        "correlation_coefficient": float(correlation),
                        "relationship_strength": "strong" if abs(correlation) > 0.7 else 
                                               "moderate" if abs(correlation) > 0.3 else "weak",
                        "relationship_direction": "positive" if correlation > 0 else "negative"
                    }
            
            insights["comparison_summary"] = f"Comparison between {metric1} and {metric2}"
            
        except Exception as e:
            insights["error"] = f"Comparison analysis failed: {str(e)}"
        
        return insights
    
    def process_json_config(self, json_config_path):
        """Process the complete JSON configuration from a file"""
        self.used_colors = set()  # Reset colors for each run
        
        if not os.path.exists(json_config_path):
            print(f"Error: JSON configuration file not found at {json_config_path}")
            return None
            
        with open(json_config_path, 'r') as f:
            config = json.load(f)
        
        results = {}
        
        # Process each section
        if "insights" in config:
            results["insights"] = self.process_insights(config["insights"])
        
        if "insights_charts" in config:
            results["insights_charts"] = self.process_insights_charts(config["insights_charts"])
        
        if "comparison" in config:
            results["comparison"] = self.process_comparison(config["comparison"])
        
        print("Processing completed!")
        print(f"Insights generated: {len(results.get('insights', []))}")
        print(f"Insights with charts generated: {len(results.get('insights_charts', []))}")
        print(f"Comparison charts generated: {len(results.get('comparison', []))}")
        
        return results

# Example usage
if __name__ == "__main__":
    # Initialize the visualization engine
    engine = HotelBookingVisualization()
    
    # Process the JSON configuration
    json_config_path = "data.json"  # Path to your JSON configuration
    results = engine.process_json_config(json_config_path)
