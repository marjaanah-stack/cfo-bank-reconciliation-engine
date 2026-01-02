import pandas as pd

def wrangler_node():
    print("🤠 The Wrangler is starting to clean the data...")

    # 1. Load the messy data we created earlier
    bank_df = pd.read_csv('bank_statement.csv')
    erp_df = pd.read_csv('erp_ledger.csv')

    # 2. Normalize Bank Dates (YYYY-MM-DD)
    bank_df['Date'] = pd.to_datetime(bank_df['Date']).dt.strftime('%Y-%m-%d')

    # 3. Normalize ERP Dates (MM/DD/YYYY)
    erp_df['Date'] = pd.to_datetime(erp_df['Date']).dt.strftime('%Y-%m-%d')

    # 4. Standardize ERP columns to match Bank columns
    # We rename 'Vendor' to 'Description' so they match
    erp_df = erp_df.rename(columns={'Vendor': 'Description'})

    # 5. Clean up descriptions (lowercase and strip spaces)
    bank_df['Description'] = bank_df['Description'].str.strip().str.upper()
    erp_df['Description'] = erp_df['Description'].str.strip().str.upper()

    # 6. Save the "Clean" versions
    bank_df.to_csv('cleaned_bank.csv', index=False)
    erp_df.to_csv('cleaned_erp.csv', index=False)

    print("✅ The Wrangler has finished! Created 'cleaned_bank.csv' and 'cleaned_erp.csv'.")

    # Display a sneak peek of the cleaned data
    print("\n--- Cleaned Bank Data Preview ---")
    print(bank_df.head(3))
    print("\n--- Cleaned ERP Data Preview ---")
    print(erp_df.head(3))

if __name__ == "__main__":
    wrangler_node()
