import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 1. Initialize the Brain
llm = ChatOpenAI(model="gpt-4o", api_key=os.environ.get("OPENAI_API_KEY"))

def matchmaker_node(bank_row, erp_df):
    """
    This node tries to match ONE bank transaction against the entire ERP.
    """
    print(f"🔍 Analyzing: {bank_row['Description']} (${bank_row['Amount']})")

    # --- Strategy A: Exact Match (Deterministic) ---
    # First, we check if the amount and description match exactly.
    exact_match = erp_df[
        (erp_df['Amount'] == bank_row['Amount']) & 
        (erp_df['Description'] == bank_row['Description'])
    ]

    if not exact_match.empty:
        return {"match_type": "EXACT", "data": exact_match.iloc[0].to_dict()}

    # --- Strategy B: The Brain (LLM Fuzzy Match) ---
    # If Strategy A fails, we ask the AI to look for "likely" matches.
    potential_vendors = erp_df['Description'].unique().tolist()

    prompt = f"""
    Bank Description: {bank_row['Description']}
    ERP Vendor List: {potential_vendors}

    Is one of these ERP vendors likely the same as the bank description? 
    Answer ONLY with the vendor name or 'NONE'.
    """

    ai_response = llm.invoke([HumanMessage(content=prompt)]).content.strip()

    if ai_response in potential_vendors:
        matched_row = erp_df[erp_df['Description'] == ai_response].iloc[0]
        return {"match_type": "FUZZY (AI)", "data": matched_row.to_dict()}

    return {"match_type": "UNMATCHED", "data": None}

def run_reconciliation():
    # Load our cleaned data
    bank_df = pd.read_csv('cleaned_bank.csv')
    erp_df = pd.read_csv('cleaned_erp.csv')

    results = []

    for _, row in bank_df.iterrows():
        match_result = matchmaker_node(row, erp_df)
        results.append({
            "Bank_Desc": row['Description'],
            "Amount": row['Amount'],
            "Status": match_result['match_type'],
            "Matched_To": match_result['data']['Description'] if match_result['data'] else "N/A"
        })

    # Show the results
    report = pd.DataFrame(results)
    print("\n--- RECONCILIATION REPORT ---")
    print(report)
    report.to_csv('recon_report.csv', index=False)

if __name__ == "__main__":
    run_reconciliation()
