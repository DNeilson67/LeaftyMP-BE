from supabase import create_client, Client
from faker import Faker
import random

# Initialize Supabase client
url = "https://rdbcbzxvtuqhnxwvdtgr.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkYmNienh2dHVxaG54d3ZkdGdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjUwMDcyMjYsImV4cCI6MjA0MDU4MzIyNn0.3F0di19jDB80khDiPn4SUEO8s_lGfG_sE581RCvkZGU"
supabase: Client = create_client(url, key)
faker = Faker()

def create_dummy_finance():
    DEFAULT_BANK_CODE = "ID_BCA"

    # Retrieve all UserIDs from the Users table
    response = supabase.table("users").select("UserID").execute()
    user_ids = response.data

    if not user_ids:
        print("No users found.")
        return

    # Update dummy finance data for each user
    for user in user_ids:
        user_id = user['UserID']
        random_account_holder = faker.name()
        random_account_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])

        # Update the centra_finance table
        update_response = supabase.table("centra_finance").update({
            "AccountHolderName": random_account_holder,
            "BankCode": DEFAULT_BANK_CODE,
            "BankAccountNumber": random_account_number
        }).eq("UserID", user_id).execute()

        # if update_response.status_code == 200:
        #     print(f"Updated finance data for UserID: {user_id}")
        # else:
        #     print(f"Failed to update UserID: {user_id}, Error: {update_response}")

    print("Dummy finance records updated successfully.")
    
if __name__ == "__main__":
    create_dummy_finance()
