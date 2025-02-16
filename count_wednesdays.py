from datetime import datetime
from dateutil import parser  # Import dateutil for automatic date parsing

input_file = "/data/dates.txt"
output_file = "/data/dates-wednesdays.txt"

try:
    with open(input_file, "r") as f:
        dates = f.readlines()

    wednesday_count = sum(
        1 for date in dates if parser.parse(date.strip()).weekday() == 2
    )

    with open(output_file, "w") as f:
        f.write(str(wednesday_count))

    print("✅ Successfully counted and saved the number of Wednesdays.")

except Exception as e:
    print(f"❌ Error processing file: {e}")
