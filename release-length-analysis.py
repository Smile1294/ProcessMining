import csv
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
import statistics

# Replace './git_log_processed.csv' with the path to your CSV file
csv_file = './git_log_processed.csv'

# Dictionary to store the latest release date for each version
release_dates = {}

with open(csv_file, 'r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            if len(row) < 6:
                continue  # Skip malformed rows
            commit_hash, tag, message, date_str, author, _ = row
            # Extract version number from tag
            if 'tag:' in tag:
                # Handle tag format variations
                tag_content = tag.strip()
                if tag_content.startswith('(tag:'):
                    version = tag_content.split('(tag:')[1].strip(')')
                else:
                    version = tag_content.split('tag:')[1].strip(')')

                # Clean version (remove any suffixes like -rc.0)
                version = version.split('-')[0]

                # Convert date string to datetime object
                # Handle timezone if present
                try:
                    date = datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # If timezone is included, ignore it
                    date = datetime.strptime(date_str.split('+')[0], '%Y-%m-%d %H:%M:%S')

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
    if len(version_parts) != 3:
        continue  # Skip versions that do not follow semantic versioning
    try:
        major, minor, patch = map(int, version_parts)
    except ValueError:
        continue  # Skip versions with non-integer parts

    # Categorize releases
    if minor == 0 and patch == 0:
        major_releases.append((version, date))
    elif patch == 0 and minor != 0:
        minor_releases.append((version, date))

# Sort the releases chronologically
major_releases.sort(key=lambda x: x[1])
minor_releases.sort(key=lambda x: x[1])

# Exclude the last major release from average calculations
if len(major_releases) > 1:
    major_releases_for_average = major_releases[:-1]  # Exclude last
else:
    major_releases_for_average = []

# Similarly, prepare the list excluding the last major release for minor mapping
major_releases_for_mapping = major_releases[:-1] if len(major_releases) > 1 else []


# Function to compute statistics for intervals
def compute_statistics(releases):
    intervals = []
    releases = sorted(releases, key=lambda x: x[1])
    for i in range(1, len(releases)):
        delta = (releases[i][1] - releases[i - 1][1]).total_seconds()
        intervals.append(delta)
    if intervals:
        avg_interval = sum(intervals) / len(intervals)
        median_interval = statistics.median(intervals)
        min_interval = min(intervals)
        max_interval = max(intervals)
        return {
            'average': avg_interval / (60 * 60 * 24),  # Convert seconds to days
            'median': median_interval / (60 * 60 * 24),
            'min': min_interval / (60 * 60 * 24),
            'max': max_interval / (60 * 60 * 24)
        }
    else:
        return None


# Calculate statistics excluding the last major release
major_stats = compute_statistics(major_releases_for_average)
minor_stats = compute_statistics(minor_releases)

# Print the statistics
if major_stats:
    print(f"Average Major Release Interval: {major_stats['average']:.2f} days")
    print(f"Median Major Release Interval: {major_stats['median']:.2f} days")
    print(f"Minimum Major Release Interval: {major_stats['min']:.2f} days")
    print(f"Maximum Major Release Interval: {major_stats['max']:.2f} days")
else:
    print("\nMajor Releases (excluding last release): Not enough major releases to calculate statistics.")

if minor_stats:
    print(f"\nAverage Minor Release interval: {minor_stats['average']:.2f} days")
    print(f"Median Minor Release interval: {minor_stats['median']:.2f} days")
    print(f"Minimum Minor Release interval: {minor_stats['min']:.2f} days")
    print(f"Maximum Minor Release interval: {minor_stats['max']:.2f} days")
else:
    print("\nMinor Releases: Not enough minor releases to calculate statistics.")

# Mapping minor releases to their corresponding major releases, excluding the last major release
minor_per_major = defaultdict(int)

# Iterate through major releases to define periods
for i, (major_version, major_date) in enumerate(major_releases_for_mapping):
    if i < len(major_releases_for_mapping) - 1:
        next_major_date = major_releases_for_mapping[i + 1][1]
    else:
        # The next major release is the last one, which is excluded from mapping
        if len(major_releases) > len(major_releases_for_mapping):
            next_major_date = major_releases[-1][1]
        else:
            next_major_date = datetime.now()  # Consider up to current date

    # Count minor releases between major_date and next_major_date
    count = 0
    for minor_version, minor_date in minor_releases:
        if major_date < minor_date < next_major_date:
            count += 1
    minor_per_major[major_version] = count

# Print the number of minor releases per major release (excluding the last major release)
if minor_per_major:
    # Compute average and median number of minor releases per major release
    minor_release_counts = list(minor_per_major.values())
    if minor_release_counts:
        average_minor_per_major = statistics.mean(minor_release_counts)
        median_minor_per_major = statistics.median(minor_release_counts)
        min_minor_per_major = min(minor_release_counts)
        max_minor_per_major = max(minor_release_counts)
        print(f"\nAverage number of minor releases per major release: {average_minor_per_major:.2f}")
        print(f"Median number of minor releases per major release: {median_minor_per_major:.2f}")
        print(f"Minimum number of minor releases per major release: {min_minor_per_major}")
        print(f"Maximum number of minor releases per major release: {max_minor_per_major}")
    else:
        print("\nNo minor releases to calculate average, median, min, and max counts.")
else:
    print("No data to display.")

# Plotting the major releases timeline
if major_releases:
    versions, dates = zip(*major_releases)
    plt.figure(figsize=(12, 6))
    plt.plot(dates, [1] * len(dates), 'o', label='Major Releases', color='blue')
    for i, version in enumerate(versions):
        plt.text(dates[i], 1.02, version, rotation=45, ha='right', va='bottom', fontsize=9)
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
    versions, dates = zip(*minor_releases)
    plt.figure(figsize=(12, 6))
    plt.plot(dates, [1] * len(dates), 'o', label='Minor Releases', color='orange')
    for i, version in enumerate(versions):
        plt.text(dates[i], 1.02, version, rotation=45, ha='right', va='bottom', fontsize=9)
    plt.yticks([])
    plt.xlabel('Date')
    plt.title('Minor Releases Timeline')
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print("No minor releases to plot.")

# Plotting the number of minor releases per major release
if minor_per_major:
    major_versions = list(minor_per_major.keys())
    counts = list(minor_per_major.values())

    plt.figure(figsize=(12, 6))
    bars = plt.bar(major_versions, counts, color='green')
    plt.xlabel('Major Release Version')
    plt.ylabel('Number of Minor Releases')
    plt.title('Number of Minor Releases per Major Release (Excluding Last Major Release)')
    plt.xticks(rotation=45)

    # Annotate bars with counts
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),  # 3 points vertical offset
                     textcoords="offset points",
                     ha='center', va='bottom')

    # Compute average, median, min, and max number of minor releases per major release
    minor_release_counts = counts
    if minor_release_counts:
        average_minor_per_major = statistics.mean(minor_release_counts)
        median_minor_per_major = statistics.median(minor_release_counts)
        min_minor_per_major = min(minor_release_counts)
        max_minor_per_major = max(minor_release_counts)

        # Plot horizontal lines for average, median, min, and max
        plt.axhline(average_minor_per_major, color='red', linestyle='--',
                    label=f'Average: {average_minor_per_major:.2f}')
        plt.axhline(median_minor_per_major, color='purple', linestyle='-.',
                    label=f'Median: {median_minor_per_major:.2f}')
        plt.axhline(min_minor_per_major, color='cyan', linestyle=':', label=f'Minimum: {min_minor_per_major}')
        plt.axhline(max_minor_per_major, color='magenta', linestyle='-', label=f'Maximum: {max_minor_per_major}')
        plt.legend()

    plt.tight_layout()
    plt.show()
else:
    print("No data to plot for minor releases per major release.")
