import pandas as pd

csv_file = "dataset/train.csv"   

new_data = {
    "qtype": "information",
    "Question": "Where can I find support groups?",
    "Answer": (
        "You can find support groups through hospitals, clinics, nonprofit organizations, and online communities. Websites like the CDC, WHO, and patient advocacy groups also list support resources by condition."
    )
}

df = pd.read_csv(csv_file)

df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
df.to_csv(csv_file, index=False)

print("✅ New entry added successfully!")
