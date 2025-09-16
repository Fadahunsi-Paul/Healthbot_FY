import pandas as pd

csv_file = "dataset/train.csv"   

new_data = {
    "qtype": "causes",
    "Question": "What are causes of malaria?",
    "Answer": (
        "Malaria is caused by Plasmodium parasites and is spread to humans through the bites of infected female Anopheles mosquitoes. After an infected mosquito bites a person, the parasite travels to the liver and then invades red blood cells, causing the disease. Although rare, malaria can also be transmitted through blood transfusions, organ donation, and from mother to child during pregnancy."
    )
}

df = pd.read_csv(csv_file)

df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
df.to_csv(csv_file, index=False)

print("✅ New entry added successfully!")
