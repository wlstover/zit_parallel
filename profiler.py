import pstats
import csv

from pathlib import Path

# Load the profile data
stats = pstats.Stats(str((Path.cwd() / 'src' / 'profile_output.prof')))

# Convert to CSV
with open('profile_results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    # Write header
    writer.writerow(['Function', 'NCalls', 'TotTime', 'PercallTot', 'CumTime', 'PercallCum', 'Filename', 'Line', 'FuncName'])
    
    # Write data
    for func, (cc, nc, tt, ct, callers) in stats.stats.items():
        filename, line, func_name = func
        writer.writerow([
            f"{filename}:{line}:{func_name}",  # Full function identifier
            nc,                                 # Number of calls
            tt,                                 # Total time
            tt/nc if nc else 0,                # Per call (total)
            ct,                                 # Cumulative time
            ct/nc if nc else 0,                # Per call (cumulative)
            filename,                          # Separate columns for easier filtering
            line,
            func_name
        ])

print("Profile data exported to profile_results.csv")