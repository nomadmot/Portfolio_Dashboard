"""
generate test daily balances
"""
import datetime
import random
import csv
from typing import List, Tuple

def generate_balance_deltas(
    start_date_str: str, 
    initial_balance: float, 
    output_filename: str = "test_daily_balances.csv"
) -> None:
    """
    Generates a series of daily random deltas, skipping weekends (Sat/Sun), 
    starting from a given date and initial balance, writing the results to a CSV file.

    Args:
        start_date_str: The starting date in 'YYYY-MM-DD' format.
        initial_balance: The starting balance.
        output_filename: The name of the CSV file to create.
    """
    
    # 1. Initialize Dates and Balance
    try:
        begin_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except ValueError:
        print("Error: Please ensure the start date is in 'YYYY-MM-DD' format.")
        return

    current_date = datetime.date.today()
    current_balance = initial_balance
    
    # List to hold the data (Date, Balance)
    data_rows: List[Tuple[str, float]] = []
    
    print("--- Starting Balance Simulation ---")
    print(f"Start Date: {begin_date}")
    print(f"Initial Balance: ${initial_balance:,.2f}")
    print(f"Simulation running until: {current_date}")

    # 2. Iterate through dates and calculate deltas
    date_iterator = begin_date
    while date_iterator <= current_date:
        
        # Check if the current day is a weekend (Saturday=5, Sunday=6)
        day_of_week = date_iterator.weekday()
        
        if day_of_week >= 5:
            #print(f"Skipping {date_iterator.strftime('%Y-%m-%d')}: Weekend day.")
            # Even if we skip the delta, we must ensure the date is recorded 
            # if we want a continuous record, but for this simulation, 
            # we only record days where activity (delta) occurs.
            date_iterator += datetime.timedelta(days=1)
            continue # Skip the rest of the loop body and move to the next date

        # --- Weekday Logic ---
        
        # Generate a random delta
        # using + or - 2% with upward bias of .5%
        delta = round(random.uniform(current_balance * -.04,
                                     current_balance * .04,),
                                     2) + (current_balance * .02)
        
        # Update the balance
        current_balance += delta
        
        # Store the result (Date formatted as string, New Balance)
        data_rows.append((date_iterator.strftime('%Y-%m-%d'), round(current_balance, 2)))
        
        # Move to the next day
        date_iterator += datetime.timedelta(days=1)

    # 3. Write results to CSV
    try:
        with open(output_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header row
            writer.writerow(['Date', 'New_Balance'])
            # Write data rows
            writer.writerows(data_rows)
        
        print("\n✅ Simulation complete!")
        print(f"Results successfully saved to {output_filename}")
        print(f"Total working days recorded: {len(data_rows)}")

    except IOError as e:
        print(f"\n❌ Error writing to file {output_filename}: {e}")


# --- Execution Example ---
if __name__ == "__main__":
    # Define your parameters here
    START_DATE = "2025-01-01"  # Change this to your desired start date
    START_BALANCE = 50000.00   # Change this to your starting balance
    
    generate_balance_deltas(START_DATE, START_BALANCE)
