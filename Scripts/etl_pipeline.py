import pandas as pd
from pathlib import Path

from datetime import datetime
log_doc = "Logs/pipeline_log.txt"

import os
from sqlalchemy import create_engine
base_dir = Path(__file__).resolve().parent

db_dir = base_dir / "Database"
db_dir.mkdir(parents=True, exist_ok=True)

database_file = db_dir / "retail_sales.db"

engine = create_engine(f"sqlite:///{database_file}")


def write_log(message):
    with open(log_doc, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")

write_log("Pipeline started")

try: 

    rawfile = Path("Raw data/retail_sales_raw.csv")
    outputfile = Path("Cleaned data/cleaned_retail_sales.csv")
    
    df = pd.read_csv(rawfile)
    
    
    print("Dataset Loaded Successfully")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    write_log(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    
    print("\nMissing Values Per Columns:")
    print(df.isnull().sum())
    
    print(f"\nDuplicate Rows Found: {df.duplicated().sum()}")
    df = df.drop_duplicates()
    write_log(f"Duplicates removed: {df.duplicated().sum()}")
    
    text_columns = ["Category", "Item", "Payment Method", "Location"]
    for i in text_columns:
        df[i] = df[i].fillna("Unknown")
        df[i] = df[i].str.strip().str.title()
    
    df["Quantity"] = df["Quantity"].fillna(1)
    
    df["Discount Applied"] = df["Discount Applied"].fillna(False)
    
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Total Spent"] = pd.to_numeric(df["Total Spent"], errors="coerce")

    mask = (
    df["Price Per Unit"].isnull() &
    df["Quantity"].notnull() &
    df["Total Spent"].notnull() &
    (df["Quantity"] != 0))

    df.loc[mask, "Price Per Unit"] = (
    df.loc[mask, "Total Spent"] / df.loc[mask, "Quantity"])   
    
    write_log("Data cleaning completed successfully")
    
    df.to_csv(outputfile, index=False)


    engine = create_engine(f"sqlite:///{database_file}")
    df.to_sql("clean_sales", con=engine, if_exists="replace", index=False)
    write_log("Data loaded into SQLite database")

    print("\nClean dataset exported successfully")
    write_log("Clean dataset exported successfully")
    write_log("Pipeline finished successfully")


    print("\nFinal dataset shape:")
    print(df.shape)



except Exception as e:
    print(f"Pipeline Failed: {e}")
    write_log(f"Pipeline failed: {e}")


