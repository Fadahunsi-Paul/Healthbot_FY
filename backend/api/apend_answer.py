import pandas as pd

# Path to your dataset
csv_file = "dataset/train.csv"   

# The new row you want to insert
new_data = {
    "qtype": "information",
    "Question": "Where can I find support groups?",
    "Answer": (
        "You can find support groups through hospitals, clinics, nonprofit organizations, and online communities. Websites like the CDC, WHO, and patient advocacy groups also list support resources by condition."
    )
}

# Load the CSV
df = pd.read_csv(csv_file)

# Append the new row
df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

# Save back to CSV
df.to_csv(csv_file, index=False)

print("✅ New entry added successfully!")
