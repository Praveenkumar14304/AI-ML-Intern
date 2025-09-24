# run_analysis.py
from cha import HotelBookingVisualization

def main():
    # Initialize the visualization engine
    engine = HotelBookingVisualization("hotel_booking.csv")
    
    # Process the JSON configuration
    json_config_path = "data.json"
    results = engine.process_json_config(json_config_path)
    
    if results:
        print(f"\n🎯 Analysis completed! Check the 'output' folder for results.")
    else:
        print(f"\n❌ Analysis failed: Config file not found.")

if __name__ == "__main__":
    main()