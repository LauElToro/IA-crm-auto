import pandas as pd

def load_leads_csv(path):
    df = pd.read_csv(path)
    return df.to_dict(orient="records")
