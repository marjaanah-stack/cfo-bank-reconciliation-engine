from fastapi import FastAPI
import uvicorn
from threading import Thread

# Initialize the API
api = FastAPI()

@api.get("/check-status")
def check_status():
    # This is what n8n will call to see if the AI is paused
    config = {"configurable": {"thread_id": "DEC_2025_RECON"}}
    state = app.get_state(config)

    if state.next:
        return {
            "status": "PAUSED",
            "at_node": state.next,
            "unmatched_items": state.values.get("unmatched_items", [])
        }
    return {"status": "RUNNING_OR_COMPLETE"}

# This function runs the API in the background
def run_api():
    uvicorn.run(api, host="0.0.0.0", port=8000)

# Start the API thread
Thread(target=run_api, daemon=True).start()
import os
import pandas as pd
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

# 1. Define the Memory Structure
class AgentState(TypedDict):
    bank_data: list
    erp_data: list
    matches: list
    unmatched_items: list  # We will store the "headaches" here

# 2. The Matchmaker Node (Now with Interrupt Logic)
def matchmaker_node(state: AgentState):
    print("🤖 Matchmaker is running...")
    bank_df = pd.DataFrame(state['bank_data'])
    erp_df = pd.DataFrame(state['erp_data'])

    current_matches = []
    current_unmatched = []

    for _, row in bank_df.iterrows():
        # Matching logic (Amount match)
        match = erp_df[erp_df['Amount'] == row['Amount']]

        if not match.empty:
            current_matches.append({"desc": row['Description'], "amount": row['Amount'], "status": "MATCHED"})
        else:
            # We found an edge case!
            current_unmatched.append({"desc": row['Description'], "amount": row['Amount']})

    return {
        "matches": current_matches, 
        "unmatched_items": current_unmatched
    }

# 3. The "Gatekeeper" Logic
def should_continue(state: AgentState):
    # If there are items that couldn't be matched, go to the 'human_review' node
    if len(state['unmatched_items']) > 0:
        return "human_review"
    return END

def human_review_node(state: AgentState):
    # This node does NOTHING. It is just a placeholder where the graph PAUSES.
    print("⏸️ PAUSED: Waiting for Maaja to review unmatched items in Slack...")
    return state

# 4. Setup Database Memory
DB_URI = os.environ.get("DATABASE_URL")
pool = ConnectionPool(conninfo=DB_URI, max_size=20)
checkpointer = PostgresSaver(pool)

import psycopg
with psycopg.connect(DB_URI, autocommit=True) as setup_conn:
    PostgresSaver(setup_conn).setup()

# 5. Build the Workflow
workflow = StateGraph(AgentState)

workflow.add_node("matchmaker", matchmaker_node)
workflow.add_node("human_review", human_review_node)

workflow.set_entry_point("matchmaker")

# Add the conditional path
workflow.add_conditional_edges(
    "matchmaker",
    should_continue,
    {
        "human_review": "human_review",
        END: END
    }
)

workflow.add_edge("human_review", END)

# CRITICAL: We tell the graph to INTERRUPT before it enters the human_review node
app = workflow.compile(checkpointer=checkpointer, interrupt_before=["human_review"])

print("✅ Graph Compiled with 'Human-in-the-Loop' safety trigger.")
if __name__ == "__main__":
    # Load the data we made earlier
    bank_list = pd.read_csv('bank_statement.csv').to_dict('records')
    erp_list = pd.read_csv('erp_ledger.csv').to_dict('records')

    # Config for the "Thread" (This is like a Ticket ID for this specific month-end)
    config = {"configurable": {"thread_id": "DEC_2025_RECON"}}

    # Start the graph
    initial_state = {"bank_data": bank_list, "erp_data": erp_list, "matches": [], "unmatched_items": []}

    for event in app.stream(initial_state, config):
        print(f"--- Node Processed: {list(event.keys())[0]} ---")

    # Check if it paused
    state = app.get_state(config)
    if state.next:
        print(f"🚨 SYSTEM ALERT: The graph has PAUSED at {state.next}. It is waiting for your approval.")