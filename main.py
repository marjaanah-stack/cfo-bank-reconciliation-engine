import pandas as pd
from datetime import datetime, timedelta

# This script creates our "messy" testing data
def generate_mock_data():
    # Dates for the transactions
    dates = [datetime(2025, 12, 1) + timedelta(days=i) for i in range(10)]

    # --- BANK DATA (The Source of Truth) ---
    bank_data = {
        'Date': [d.strftime('%Y-%m-%d') for d in dates],
        'Description': [
            'STRIPE TRANSFER - 8329', 'ADOBE *SUBSCRIPTION', 'GOOGLE *GSUITE_FINTECH',
            'AMZN MKTP US', ' landlord_payment_dec', 'REPLIT.COM AI CHRGE',
            'SUDO_SUBSCRIPTION', 'WFB_INTEREST', 'STRIPE TRANSFER - 9102', 'MISC_CREDIT'
        ],
        'Amount': [4500.00, -52.99, -120.00, -215.50, -3200.00, -20.00, -15.00, 0.45, 1200.00, 50.00]
    }

    # --- ERP DATA (The Messy Books) ---
    erp_data = {
        'Date': [(datetime(2025, 12, 1) + timedelta(days=i, hours=2)).strftime('%m/%d/%Y') for i in range(10)],
        'Vendor': [
            'Stripe Inc', 'Adobe Systems', 'Google Cloud',
            'Amazon.com', 'Office Rent', 'Replit Inc',
            'Sudo', 'Wells Fargo', 'Stripe Inc', 'Unknown Credit'
        ],
        'Amount': [4500.00, -52.99, -120.00, -215.50, -3200.00, -20.00, -15.00, 0.00, 1200.00, 50.00] 
    }

    # Save to CSV files
    pd.DataFrame(bank_data).to_csv('bank_statement.csv', index=False)
    pd.DataFrame(erp_data).to_csv('erp_ledger.csv', index=False)

    print("✅ Success! 'bank_statement.csv' and 'erp_ledger.csv' created.")

if __name__ == "__main__":
    generate_mock_data()