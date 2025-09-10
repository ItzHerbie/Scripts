This script grabs a list of computer from a text file called computers.txt and check to see if they exist in Active Directory (AD) using DSQUERY. If the computer exists in AD it will return 'Ture, if it does not exist it returns 'False"
```python
import subprocess
import csv

# Input and output files
input_file = "computers.txt" #Place Computers names in a .txt file. One machine name per line. Store in the same directory as script.
output_file = "computer_states.csv"

def check_computer_in_ad(computer_name):
    try:
        result = subprocess.run(
            ['dsquery', 'computer', '-name', computer_name],
            capture_output=True, text=True, timeout=5
        )
        # Case-insensitive exact match on CN=
        for line in result.stdout.strip().splitlines():
            if f"CN={computer_name}".lower() in line.strip().lower():
                return True
        return False
    except Exception as e:
        print(f"Error checking {computer_name}: {e}")
        return False

# Open input and output files
with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = infile.read().splitlines()
    writer = csv.writer(outfile)
    writer.writerow(['MachineName', 'State'])  # Header

    for name in reader:
        name = name.strip()
        if not name:
            continue
        exists = check_computer_in_ad(name)
        print(f"{name}: {'True' if exists else 'False'}")
        writer.writerow([name, exists])

print(f"\nDone. Results saved to: {output_file}")
