import json
import matplotlib.pyplot as plt
import numpy as np

# Load MongoDB and SQL performance logs
with open('mongo_logs_new.json', 'r') as mongo_file:
    mongo_logs = json.load(mongo_file)

with open('sql_logs_new.json', 'r') as sql_file:
    sql_logs = json.load(sql_file)

# Prepare data for visualization
data_sizes = [10, 100, 1000, 10000]
operations = [
    'insert_entities_batch',
    'insert_entities_batch_simple',
    'fetch_anime_simple',
    'fetch_anime_with_relations',
    'delete_anime_with_relations'
]

# Create visualization
plt.figure(figsize=(20, 15))
plt.suptitle('Performance Comparison: MongoDB vs SQL', fontsize=16)

# Color scheme
mongo_color = 'blue'
sql_color = 'red'

# Subplot for each operation
for idx, operation in enumerate(operations, 1):
    plt.subplot(3, 2, idx)

    # Prepare data for MongoDB and SQL
    mongo_avgs = []
    sql_avgs = []

    for entry in mongo_logs:
        if operation in entry['performance_stats']:
            mongo_avgs.append(entry['performance_stats'][operation]['avg'])

    for entry in sql_logs:
        if operation in entry['performance_stats']:
            sql_avgs.append(entry['performance_stats'][operation]['avg'])

    # Plot comparison
    plt.plot(data_sizes, mongo_avgs, marker='o', color=mongo_color, label='MongoDB')
    plt.plot(data_sizes, sql_avgs, marker='s', color=sql_color, label='SQL')

    plt.title(f'Performance: {operation}', fontsize=10)
    plt.xlabel('Data Size', fontsize=8)
    plt.ylabel('Average Time (seconds)', fontsize=8)
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend()

plt.tight_layout()
plt.savefig('performance_comparison.png')
plt.close()

# Print out some key observations
print("Performance Comparison Summary:")
for operation in operations:
    print(f"\n{operation}:")
    for size, mongo_entry, sql_entry in zip(data_sizes, mongo_logs, sql_logs):
        mongo_avg = mongo_entry['performance_stats'][operation]['avg']
        sql_avg = sql_entry['performance_stats'][operation]['avg']
        print(f"Data Size {size}:")
        print(f"  MongoDB Average: {mongo_avg:.4f} seconds")
        print(f"  SQL Average:     {sql_avg:.4f} seconds")
        print(f"  {'MongoDB Faster' if mongo_avg < sql_avg else 'SQL Faster'}")