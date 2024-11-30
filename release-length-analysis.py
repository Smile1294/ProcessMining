import csv
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

# Replace 'releases.csv' with the path to your CSV file
csv_file = './git_log_processed.csv'

# Dictionaries to store the latest release date for each version
release_dates = {}

with open(csv_file, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            if len(row) < 6:
                continue  # Skip malformed rows
            commit_hash, tag, message, date_str, author, _ = row
            # Extract version number from tag
            if 'tag:' in tag:
                version = tag.strip().split('(tag:')[1].strip(')')
                # Convert date string to datetime object
                date = datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')
                # Update the release date if this is the latest commit for the version
                if version not in release_dates or date > release_dates[version]:
                    release_dates[version] = date
        except Exception as e:
            print(f"Error processing row: {row}")
            print(f"Exception: {e}")

# Lists to store major and minor releases
major_releases = []
minor_releases = []

for version, date in release_dates.items():
    version_parts = version.split('.')
    if len(version_parts) == 3:
        try:
            major, minor, patch = version_parts
            major = int(major)
            minor = int(minor)
            patch = int(patch)
            # Categorize releases
            if minor == 0 and patch == 0:
                major_releases.append((version, date))
            elif patch == 0 and minor != 0:
                minor_releases.append((version, date))
        except:
            print(f"Error processing version: {version}")

# Function to compute average time between releases
def average_interval(releases):
    intervals = []
    releases = sorted(releases, key=lambda x: x[1])
    for i in range(1, len(releases)):
        delta = (releases[i][1] - releases[i-1][1]).total_seconds()
        intervals.append(delta)
    if intervals:
        avg_interval = sum(intervals) / len(intervals)
        return avg_interval / (60*60*24)  # Convert seconds to days
    else:
        return None

# Calculate average intervals
avg_major_interval = average_interval(major_releases)
avg_minor_interval = average_interval(minor_releases)

if avg_major_interval is not None:
    print(f"Average time between major releases: {avg_major_interval:.2f} days")
else:
    print("Not enough major releases to calculate average interval.")

if avg_minor_interval is not None:
    print(f"Average time between minor releases: {avg_minor_interval:.2f} days")
else:
    print("Not enough minor releases to calculate average interval.")

# Plotting the major releases timeline
if major_releases:
    versions, dates = zip(*sorted(major_releases, key=lambda x: x[1]))
    plt.figure(figsize=(10, 5))
    plt.plot(dates, [1]*len(dates), 'o', label='Major Releases')
    for i, version in enumerate(versions):
        plt.text(dates[i], 1.02, version, rotation=45, ha='right')
    plt.yticks([])
    plt.xlabel('Date')
    plt.title('Major Releases Timeline')
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print("No major releases to plot.")

# Plotting the minor releases timeline
if minor_releases:
    versions, dates = zip(*sorted(minor_releases, key=lambda x: x[1]))
    plt.figure(figsize=(10, 5))
    plt.plot(dates, [1]*len(dates), 'o', label='Minor Releases', color='orange')
    for i, version in enumerate(versions):
        plt.text(dates[i], 1.02, version, rotation=45, ha='right')
    plt.yticks([])
    plt.xlabel('Date')
    plt.title('Minor Releases Timeline')
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print("No minor releases to plot.")
