import csv

###Variables for Serial Generation
ITEM_TOTE = "10"
ITEM_ROBOT = "11"
ITEM_BAG = "21"
OUTPUT_CSV = "production_bags.csv"
LABEL_COUNT = 200
LABEL_START_NUM = 101

def calculate_pure_mod97(base_string):
    """Calculates the pure remainder (Modulo 97)."""
    # Remove spaces and treat the entire string as one large integer
    numeric_only = base_string.replace(" ", "")
    remainder = int(numeric_only) % 97
    # Return as a 2-digit string (e.g., 07)
    return f"{remainder:02d}"

def generate_serials(count):
    filename = OUTPUT_CSV
    header = ["qr_data"]
    
    # Format: 01 11 000 01XXXXX 00 CS
    #prefix = "01 21 000"
    prefix = f"01 {ITEM_BAG} 000"
    suffix_fixed = "00"
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        
        for i in range(LABEL_START_NUM, count + 1):
            # 01XXXXX format with 5 digits for the 'X' count
            # This results in a 7-digit block: '01' + '00001'
            serial_int_field = f"01{i:05d}"
            
            # Construct the base string
            base_str = f"{prefix} {serial_int_field} {suffix_fixed}"
            
            # Calculate pure remainder checksum
            cs = calculate_pure_mod97(base_str)
            
            # Final assembly
            full_serial = f"{base_str} {cs}"
            writer.writerow([full_serial])

    print(f"Success! {count} serials saved to {filename}")

if __name__ == "__main__":
    
    generate_serials(LABEL_COUNT)