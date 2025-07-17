import hashlib
import json
import os
import pandas as pd
import streamlit as st
from datetime import datetime

# Blockchain Class for Expense Tracking
class Blockchain:
    def __init__(self, filename="blockchain.json"):
        self.filename = filename
        self.pending_transactions = []
        if os.path.exists(filename):
            self.load_blockchain()
        else:
            self.chain = []
            self.create_block(previous_hash='0')  # Genesis block

    def save_blockchain(self):
        with open(self.filename, 'w') as f:
            json.dump(self.chain, f)

    def load_blockchain(self):
        with open(self.filename, 'r') as f:
            self.chain = json.load(f)

    def create_block(self, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.now()),
            'transactions': self.pending_transactions,
            'previous_hash': previous_hash
        }
        block['hash'] = self.hash_block(block)
        self.chain.append(block)
        self.pending_transactions = []
        self.save_blockchain()  # Save to JSON
        return block

    def hash_block(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_transaction(self, user_id, date, category, amount, description):
        transaction = {
            'user_id': user_id,
            'date': date,
            'category': category,
            'amount': amount,
            'description': description
        }
        self.pending_transactions.append(transaction)
        return transaction

# Streamlit App for User Interface
st.title("Student Budget Blockchain Tracker")
st.write("Track your expenses securely with blockchain technology")

# Initialize Blockchain
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain()

# Input Form for Expenses
st.header("Add New Expense")
with st.form("expense_form"):
    user_id = st.text_input("User ID (e.g., john123)")
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Transportation", "Entertainment", "Others"])
    amount = st.number_input("Amount (TWD)", min_value=0.0, step=0.01)
    description = st.text_input("Description")
    submit = st.form_submit_button("Add Expense")

    if submit:
        if not user_id:
            st.error("Please enter a User ID")
        else:
            st.session_state.blockchain.add_transaction(
                user_id=user_id,
                date=str(date),
                category=category,
                amount=amount,
                description=description
            )
            st.session_state.blockchain.create_block(
                previous_hash=st.session_state.blockchain.chain[-1]['hash'] if st.session_state.blockchain.chain else '0'
            )
            st.success("Expense added and recorded in blockchain!")

# Display Blockchain
st.header("Blockchain Ledger")
if st.session_state.blockchain.chain:
    for block in st.session_state.blockchain.chain:
        st.write(f"Block #{block['index']}")
        st.write(f"Timestamp: {block['timestamp']}")
        st.write("Transactions:")
        st.json(block['transactions'])
        st.write(f"Block Hash: {block['hash']}")
        st.write(f"Previous Hash: {block['previous_hash']}")
        st.write("---")

# Data Analysis and Export
st.header("Expense Analysis")
if st.session_state.blockchain.chain:
    transactions = []
    for block in st.session_state.blockchain.chain:
        transactions.extend(block['transactions'])
    
    if transactions:
        df = pd.DataFrame(transactions)
        st.write("Expense Summary by Category:")
        summary = df.groupby(['user_id', 'category'])['amount'].sum().reset_index()
        st.dataframe(summary)

        # Filter by User ID
        user_filter = st.selectbox("Filter by User ID", ['All'] + sorted(df['user_id'].unique().tolist()))
        if user_filter != 'All':
            df = df[df['user_id'] == user_filter]
        
        st.write("Filtered Transactions:")
        st.dataframe(df)

        # Export to CSV for Tableau visualization
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name="expenses.csv",
            mime="text/csv"
        )