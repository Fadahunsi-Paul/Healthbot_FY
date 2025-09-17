import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(__file__))
IN_CSV = os.path.join(BASE, 'exports', 'answerable_questions.csv')
OUT_CSV = os.path.join(BASE, 'api', 'dataset', 'train_augmented.csv')


def main():
    df = pd.read_csv(IN_CSV)
    # Keep only question, qtype, answer; ensure columns match train.csv schema
    out = df[['question', 'qtype', 'answer']].rename(columns={
        'question': 'Question',
        'qtype': 'qtype',
        'answer': 'Answer',
    })
    # Drop exact duplicates
    out = out.drop_duplicates()
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    print(f'Wrote augmented dataset with {len(out)} rows to {OUT_CSV}')


if __name__ == '__main__':
    main()
