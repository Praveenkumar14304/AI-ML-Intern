import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
from collections import Counter

class InsightGenerator:
    def __init__(self, output_dir="output", plots_dir="plots"):
        self.output_dir = output_dir
        self.plots_dir = plots_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(plots_dir, exist_ok=True)
        
    def process_features(self, df, column_types, return_json=True, save_json=True):
        """
        Main method to process features and generate insights
        
        Parameters:
        df: DataFrame with the data
        column_types: Dictionary with column names as keys and their types as values
        return_json: Whether to return JSON results
        save_json: Whether to save JSON results to file
        
        Returns:
        Dictionary with insights if return_json=True, else None
        """
        results = {}
        
        for column, col_type in column_types.items():
            if column not in df.columns:
                print(f"Warning: Column {column} not found in DataFrame")
                continue
                
            column_data = df[column].dropna()
            if len(column_data) == 0:
                print(f"Warning: Column {column} has no data after dropping NaN values")
                continue
                
            # Process based on column type
            if col_type == 'numerical':
                results[column] = self.process_numerical(column_data, column)
            elif col_type == 'categorical':
                results[column] = self.process_categorical(column_data, column)
            elif col_type == 'datetime':
                results[column] = self.process_datetime(column_data, column)
            elif col_type == 'text':
                results[column] = self.process_text(column_data, column)
            else:
                print(f"Warning: Unknown column type {col_type} for column {column}")
        
        # Handle output options
        if save_json:
            self.save_results(results)
            
        return results if return_json else None
    
    def process_numerical(self, data, column_name):
        """Process numerical columns"""
        # Calculate statistics
        stats = {
            'mean': float(data.mean()),
            'median': float(data.median()),
            'std': float(data.std()),
            'min': float(data.min()),
            'max': float(data.max()),
            'q1': float(data.quantile(0.25)),
            'q3': float(data.quantile(0.75)),
            'iqr': float(data.quantile(0.75) - data.quantile(0.25)),
            'outlier_percent': self.calculate_outlier_percentage(data)
        }
        
        # Generate insight
        insight = self.generate_numerical_insight(data, column_name, stats)
        
        # Generate plot
        plot_path = self.create_numerical_plot(data, column_name)
        
        return {
            'type': 'numerical',
            'statistics': stats,
            'insight': insight,
            'plot_path': plot_path
        }
    
    def process_categorical(self, data, column_name):
        """Process categorical columns"""
        # Calculate statistics
        value_counts = data.value_counts()
        stats = {
            'unique_values': int(len(value_counts)),
            'value_counts': value_counts.to_dict(),
            'most_frequent': value_counts.index[0] if len(value_counts) > 0 else None,
            'most_frequent_percentage': float(value_counts.iloc[0] / len(data) * 100) if len(value_counts) > 0 else 0
        }
        
        # Generate insight
        insight = self.generate_categorical_insight(data, column_name, stats)
        
        # Generate plot
        plot_path = self.create_categorical_plot(data, column_name)
        
        return {
            'type': 'categorical',
            'statistics': stats,
            'insight': insight,
            'plot_path': plot_path
        }
    
    def process_datetime(self, data, column_name):
        """Process datetime columns"""
        # Convert to datetime if not already
        datetime_data = pd.to_datetime(data)
        
        # Calculate statistics
        stats = {
            'start_date': str(datetime_data.min()),
            'end_date': str(datetime_data.max()),
            'date_range_days': int((datetime_data.max() - datetime_data.min()).days),
            'unique_dates': int(datetime_data.nunique()),
            'most_frequent_date': str(datetime_data.value_counts().index[0]) if len(datetime_data) > 0 else None,
            'avg_gap_days': self.calculate_avg_date_gap(datetime_data)
        }
        
        # Generate insight
        insight = self.generate_datetime_insight(datetime_data, column_name, stats)
        
        # Generate plot
        plot_path = self.create_datetime_plot(datetime_data, column_name)
        
        return {
            'type': 'datetime',
            'statistics': stats,
            'insight': insight,
            'plot_path': plot_path
        }
    
    def process_text(self, data, column_name):
        """Process text columns"""
        # Calculate statistics
        word_counts = self.analyze_text_content(data)
        stats = {
            'total_entries': int(len(data)),
            'avg_word_count': float(np.mean([len(str(text).split()) for text in data])),
            'unique_words': int(len(word_counts)),
            'most_common_words': dict(word_counts.most_common(5))
        }
        
        # Generate insight
        insight = self.generate_text_insight(data, column_name, stats)
        
        # Generate plot
        plot_path = self.create_text_plot(data, column_name)
        
        return {
            'type': 'text',
            'statistics': stats,
            'insight': insight,
            'plot_path': plot_path
        }
    
    def calculate_outlier_percentage(self, data):
        """Calculate percentage of outliers using IQR method"""
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        return float(len(outliers) / len(data) * 100)
    
    def calculate_avg_date_gap(self, datetime_data):
        """Calculate average gap between dates"""
        if len(datetime_data) < 2:
            return 0
        sorted_dates = datetime_data.sort_values()
        gaps = (sorted_dates.shift(-1) - sorted_dates).dropna()
        return float(gaps.mean().days) if not gaps.empty else 0
    
    def analyze_text_content(self, text_data):
        """Analyze text content and return word frequencies"""
        all_text = ' '.join(text_data.astype(str))
        words = all_text.lower().split()
        # Remove common stop words and short words
        stop_words = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'an', 'for', 'on', 'with', 'as', 'by', 'at'}
        words = [word for word in words if len(word) > 2 and word not in stop_words]
        return Counter(words)
    
    def generate_numerical_insight(self, data, column_name, stats):
        """Generate meaningful insight for numerical data"""
        insight = f"The {column_name} feature has a mean of {stats['mean']:.2f} and median of {stats['median']:.2f}. "
        insight += f"Values range from {stats['min']:.2f} to {stats['max']:.2f} with a standard deviation of {stats['std']:.2f}. "
        
        if stats['outlier_percent'] > 5:
            insight += f"Notably, {stats['outlier_percent']:.1f}% of values are outliers. "
        
        # Add business context based on column name
        if 'salary' in column_name.lower():
            insight += "This salary distribution reflects multiple job levels and experience tiers within the organization."
        elif 'age' in column_name.lower():
            insight += "The age distribution shows the demographic spread of the population being analyzed."
        else:
            insight += "The distribution pattern provides insights into the variability of this metric."
            
        return insight
    
    def generate_categorical_insight(self, data, column_name, stats):
        """Generate meaningful insight for categorical data"""
        insight = f"The {column_name} feature has {stats['unique_values']} unique values. "
        insight += f"The most frequent value is '{stats['most_frequent']}' which appears in {stats['most_frequent_percentage']:.1f}% of records. "
        
        # Add business context based on column name
        if 'department' in column_name.lower():
            insight += "This distribution reflects the organizational structure and department sizes."
        elif 'city' in column_name.lower():
            insight += "Geographic distribution shows concentration in specific locations."
        else:
            insight += "The value distribution indicates the prevalence of different categories."
            
        return insight
    
    def generate_datetime_insight(self, data, column_name, stats):
        """Generate meaningful insight for datetime data"""
        insight = f"The {column_name} feature spans {stats['date_range_days']} days from {stats['start_date']} to {stats['end_date']}. "
        insight += f"There are {stats['unique_dates']} unique dates with an average gap of {stats['avg_gap_days']:.1f} days between entries. "
        
        # Add business context based on column name
        if 'signup' in column_name.lower():
            insight += "This timeline shows customer acquisition patterns over time."
        elif 'purchase' in column_name.lower():
            insight += "Purchase dates reveal buying patterns and potential seasonal trends."
        else:
            insight += "The temporal distribution provides insights into activity patterns over time."
            
        return insight
    
    def generate_text_insight(self, data, column_name, stats):
        """Generate meaningful insight for text data"""
        insight = f"The {column_name} feature contains {stats['total_entries']} entries with an average of {stats['avg_word_count']:.1f} words each. "
        insight += f"There are {stats['unique_words']} unique words across all entries. "
        
        # Mention most common words if available
        if stats['most_common_words']:
            common_words = list(stats['most_common_words'].keys())
            insight += f"The most common words are: {', '.join(common_words)}. "
        
        # Add business context based on column name
        if 'review' in column_name.lower() or 'feedback' in column_name.lower():
            insight += "This text data provides valuable customer sentiment and feedback."
        elif 'description' in column_name.lower():
            insight += "The content describes key features and characteristics of the items."
        else:
            insight += "The text content offers qualitative insights into the dataset."
            
        return insight
    
    def create_numerical_plot(self, data, column_name):
        """Create appropriate plot for numerical data"""
        plt.figure(figsize=(10, 6))
        
        # Choose plot type based on data characteristics
        if self.calculate_outlier_percentage(data) > 5:
            # Use box plot if there are outliers
            sns.boxplot(y=data)
            plot_type = 'box'
        else:
            # Use histogram for normal distribution
            sns.histplot(data, kde=True)
            plot_type = 'histogram'
        
        plt.title(f'{column_name} Distribution')
        plot_path = os.path.join(self.plots_dir, f'{column_name}_{plot_type}.png')
        plt.savefig(plot_path)
        plt.close()
        
        return plot_path
    
    def create_categorical_plot(self, data, column_name):
        """Create appropriate plot for categorical data"""
        plt.figure(figsize=(10, 6))
        
        value_counts = data.value_counts()
        
        # Choose plot type based on number of categories
        if len(value_counts) <= 5:
            # Use pie chart for small number of categories
            plt.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
            plot_type = 'pie'
        else:
            # Use bar chart for many categories
            if len(value_counts) > 10:
                # Show only top 10 categories
                value_counts = value_counts.head(10)
            
            sns.barplot(x=value_counts.values, y=value_counts.index)
            plot_type = 'bar'
        
        plt.title(f'{column_name} Distribution')
        plot_path = os.path.join(self.plots_dir, f'{column_name}_{plot_type}.png')
        plt.savefig(plot_path)
        plt.close()
        
        return plot_path
    
    def create_datetime_plot(self, data, column_name):
        """Create appropriate plot for datetime data"""
        plt.figure(figsize=(10, 6))
        
        # Convert to date for counting
        date_counts = data.dt.date.value_counts().sort_index()
        
        # Use line plot for time series
        plt.plot(date_counts.index, date_counts.values)
        plt.xticks(rotation=45)
        plt.title(f'{column_name} Timeline')
        
        plot_type = 'timeline'
        plot_path = os.path.join(self.plots_dir, f'{column_name}_{plot_type}.png')
        plt.savefig(plot_path)
        plt.close()
        
        return plot_path
    
    def create_text_plot(self, data, column_name):
        """Create appropriate plot for text data"""
        plt.figure(figsize=(10, 6))
        
        # Analyze word frequencies
        word_counts = self.analyze_text_content(data)
        
        # Use bar chart for top words
        top_words = word_counts.most_common(10)
        words, counts = zip(*top_words)
        
        sns.barplot(x=list(counts), y=list(words))
        plt.title(f'Top Words in {column_name}')
        
        plot_type = 'word_frequency'
        plot_path = os.path.join(self.plots_dir, f'{column_name}_{plot_type}.png')
        plt.savefig(plot_path)
        plt.close()
        
        return plot_path
    
    def save_results(self, results):
        """Save results to JSON file"""
        output_path = os.path.join(self.output_dir, 'analysis_insights.json')
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, (np.integer, np.int32, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Timestamp):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            else:
                return obj
        
        serializable_results = convert_types(results)
        
        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=4)
        
        print(f"Results saved to {output_path}")


# Example usage
if __name__ == "__main__":
    # Sample data creation for testing
    np.random.seed(42)
    sample_data = {
        'age': np.random.randint(18, 65, 100),
        'salary': np.random.normal(50000, 15000, 100),
        'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing', 'Sales'], 100),
        'city': np.random.choice(['New York', 'London', 'Tokyo', 'Paris', 'Sydney'], 100),
        'signup_date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'customer_review': np.random.choice([
            'Great product! Very satisfied with the quality.',
            'Poor experience. The product did not meet expectations.',
            'Average product. Nothing special but gets the job done.',
            'Excellent quality! Would highly recommend.',
            'Disappointed with the purchase. Not worth the price.'
        ], 100)
    }
    
    df = pd.DataFrame(sample_data)
    
    # Define column types (this would come from previous processing steps)
    column_types = {
        'age': 'numerical',
        'salary': 'numerical',
        'department': 'categorical',
        'city': 'categorical',
        'signup_date': 'datetime',
        'customer_review': 'text'
    }
    
    # Initialize and run the insight generator
    generator = InsightGenerator()
    results = generator.process_features(df, column_types, return_json=True, save_json=True)
    
    # Print sample insights
    print("Sample Insights:")
    for column, data in list(results.items())[:3]:
        print(f"\n{column}: {data['insight']}")