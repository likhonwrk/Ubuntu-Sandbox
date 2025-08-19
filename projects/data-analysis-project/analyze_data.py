import pandas as pd
import matplotlib.pyplot as plt
import os

def analyze_sales_data():
    """
    Analyzes sales data and generates a plot.
    """
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the CSV file
    csv_path = os.path.join(script_dir, 'sales_data.csv')

    # Check if the data file exists
    if not os.path.exists(csv_path):
        print(f"Error: Data file not found at {csv_path}")
        return

    try:
        # Read the data
        df = pd.read_csv(csv_path)

        # Perform analysis: total sales per product
        sales_by_product = df.groupby('Product')['Sales'].sum()

        # Create a plot
        plt.figure(figsize=(10, 6))
        sales_by_product.plot(kind='bar', color=['#3498db', '#2ecc71', '#e74c3c'])
        plt.title('Total Sales by Product')
        plt.xlabel('Product')
        plt.ylabel('Total Sales')
        plt.xticks(rotation=0)
        plt.grid(axis='y', linestyle='--')

        # Save the plot
        plot_path = os.path.join(script_dir, 'sales_by_product.png')
        plt.savefig(plot_path)

        print(f"Analysis complete. Plot saved to {plot_path}")

    except Exception as e:
        print(f"An error occurred during analysis: {e}")

if __name__ == "__main__":
    analyze_sales_data()
