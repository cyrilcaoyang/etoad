"""
This script runs designated scripts in the current directory.
"""

script_list = [
    # "echem_SWV_cyclic_scans.py",
    "echem_CV_multi_scan_rates.py",
    "echem_CV_const_scan_rate.py",
    "sampler_wash_refill.py"
]

for script in script_list:
    print(f"Running {script}...")
    try:
        # Import and run the current script
        exec(open(script).read())
        print(f"{script} executed successfully.")
    except Exception as e:
        print(f"Error running {script}: {e}")

print("All scripts executed.")