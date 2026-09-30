import json

def dataframe_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

def plan_to_json(plan):
    return json.dumps(plan, indent=2, ensure_ascii=False)
