"""
Script to find products that are 'Reserved' but belong to expired transactions.
This identifies products that should have been released when transactions expired.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import *

def get_database_url():
    """Get database URL from environment variables"""
    # Use the same POSTGRESQL_URL as in database.py
    postgresql_url = os.getenv("POSTGRESQL_URL")
    
    if not postgresql_url:
        # Fallback to manual construction if POSTGRESQL_URL is not set
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "leafty")
        db_user = os.getenv("DB_USER", "postgres")
        db_pass = os.getenv("DB_PASSWORD", "password")
        postgresql_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    
    return postgresql_url

def find_orphaned_products():
    """Find products that are Reserved but belong to expired transactions"""
    
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    print("🔍 Searching for orphaned products (Reserved but transaction expired)...")
    print("=" * 70)
    
    # Query to find orphaned products across all product types
    query = text("""
    -- Find products that are 'Reserved' but transaction is expired
    WITH expired_transactions AS (
        SELECT 
            t."TransactionID",
            t."ExpirationAt",
            t."TransactionStatus",
            t."CustomerID"
        FROM transactions t
        WHERE t."ExpirationAt" < NOW()
        AND t."TransactionStatus" IN ('Transaction Pending', 'Payment Pending')
    ),
    orphaned_products AS (
        -- Wet Leaves
        SELECT 
            'wet_leaves' as product_type,
            wl."WetLeavesID" as product_id,
            wl."Status" as current_status,
            wl."UserID" as centra_id,
            ms."Price",
            wl."Weight",
            et."TransactionID",
            et."ExpirationAt",
            et."TransactionStatus",
            et."CustomerID",
            u."Username" as centra_name,
            cu."Username" as customer_name,
            EXTRACT(EPOCH FROM (NOW() - et."ExpirationAt")) / 3600 as hours_since_expired
        FROM expired_transactions et
        JOIN sub_transactions st ON et."TransactionID" = st."TransactionID"
        JOIN market_shipments ms ON st."SubTransactionID" = ms."SubTransactionID"
        JOIN wet_leaves wl ON ms."ProductID" = wl."WetLeavesID"
        JOIN users u ON wl."UserID" = u."UserID"
        JOIN users cu ON et."CustomerID" = cu."UserID"
        WHERE ms."ProductTypeID" = 1
        AND wl."Status" = 'Reserved'
        
        UNION ALL
        
        -- Dry Leaves
        SELECT 
            'dry_leaves' as product_type,
            dl."DryLeavesID" as product_id,
            dl."Status" as current_status,
            dl."UserID" as centra_id,
            ms."Price",
            dl."Processed_Weight" as "Weight",
            et."TransactionID",
            et."ExpirationAt",
            et."TransactionStatus",
            et."CustomerID",
            u."Username" as centra_name,
            cu."Username" as customer_name,
            EXTRACT(EPOCH FROM (NOW() - et."ExpirationAt")) / 3600 as hours_since_expired
        FROM expired_transactions et
        JOIN sub_transactions st ON et."TransactionID" = st."TransactionID"
        JOIN market_shipments ms ON st."SubTransactionID" = ms."SubTransactionID"
        JOIN dry_leaves dl ON ms."ProductID" = dl."DryLeavesID"
        JOIN users u ON dl."UserID" = u."UserID"
        JOIN users cu ON et."CustomerID" = cu."UserID"
        WHERE ms."ProductTypeID" = 2
        AND dl."Status" = 'Reserved'
        
        UNION ALL
        
        -- Flour (Powder)
        SELECT 
            'flour' as product_type,
            f."FlourID" as product_id,
            f."Status" as current_status,
            f."UserID" as centra_id,
            ms."Price",
            f."Flour_Weight" as "Weight",
            et."TransactionID",
            et."ExpirationAt",
            et."TransactionStatus",
            et."CustomerID",
            u."Username" as centra_name,
            cu."Username" as customer_name,
            EXTRACT(EPOCH FROM (NOW() - et."ExpirationAt")) / 3600 as hours_since_expired
        FROM expired_transactions et
        JOIN sub_transactions st ON et."TransactionID" = st."TransactionID"
        JOIN market_shipments ms ON st."SubTransactionID" = ms."SubTransactionID"
        JOIN flour f ON ms."ProductID" = f."FlourID"
        JOIN users u ON f."UserID" = u."UserID"
        JOIN users cu ON et."CustomerID" = cu."UserID"
        WHERE ms."ProductTypeID" = 3
        AND f."Status" = 'Reserved'
    )
    SELECT 
        product_type,
        product_id,
        current_status,
        centra_name,
        customer_name,
        "Price",
        "Weight",
        "TransactionID",
        "ExpirationAt",
        "TransactionStatus",
        ROUND(hours_since_expired::numeric, 2) as hours_since_expired
    FROM orphaned_products
    ORDER BY hours_since_expired DESC, product_type, product_id;
    """)
    
    try:
        # Execute the query
        with engine.connect() as connection:
            result = connection.execute(query)
            orphaned_products = result.fetchall()
            
            if not orphaned_products:
                print("✅ No orphaned products found! All products are properly managed.")
                return
            
            # Convert to DataFrame for better display
            df = pd.DataFrame(orphaned_products, columns=[
                'Product Type', 'Product ID', 'Current Status', 'Centra Name', 
                'Customer Name', 'Price', 'Weight', 'Transaction ID', 
                'Expiration Date', 'Transaction Status', 'Hours Since Expired'
            ])
            
            print(f"🚨 Found {len(orphaned_products)} orphaned products:")
            print()
            
            # Summary by product type
            summary = df.groupby('Product Type').agg({
                'Product ID': 'count',
                'Price': 'sum',
                'Weight': 'sum',
                'Hours Since Expired': ['min', 'max', 'mean']
            }).round(2)
            
            print("📊 SUMMARY BY PRODUCT TYPE:")
            print(summary)
            print()
            
            # Show most critical cases (oldest expired)
            print("🔥 TOP 10 MOST CRITICAL CASES (Longest Expired):")
            print(df.head(10).to_string(index=False))
            print()
            
            # Show by centra
            print("🏪 AFFECTED CENTRAS:")
            centra_summary = df.groupby('Centra Name').agg({
                'Product ID': 'count',
                'Price': 'sum',
                'Hours Since Expired': 'mean'
            }).round(2).sort_values('Product ID', ascending=False)
            print(centra_summary)
            print()
            
            # Generate release SQL commands
            print("🛠️  SQL COMMANDS TO RELEASE THESE PRODUCTS:")
            print("=" * 50)
            
            for product_type in df['Product Type'].unique():
                products = df[df['Product Type'] == product_type]
                product_ids = products['Product ID'].tolist()
                
                if product_type == 'wet_leaves':
                    table_name = 'wet_leaves'
                    id_field = '"WetLeavesID"'
                elif product_type == 'dry_leaves':
                    table_name = 'dry_leaves'
                    id_field = '"DryLeavesID"'
                elif product_type == 'flour':
                    table_name = 'flour'
                    id_field = '"FlourID"'
                
                print(f"-- Release {len(product_ids)} {product_type.replace('_', ' ').title()} products")
                print(f"UPDATE {table_name}")
                print(f"SET \"Status\" = 'Awaiting'")
                print(f"WHERE {id_field} IN ({', '.join(map(str, product_ids))})")
                print(f"AND \"Status\" = 'Reserved';")
                print()
            
            # Transaction cleanup
            expired_transaction_ids = df['Transaction ID'].unique()
            print("-- Update expired transaction statuses")
            print("UPDATE transactions")
            print("SET \"TransactionStatus\" = 'Transaction Expired'")
            transaction_ids_str = "', '".join(expired_transaction_ids)
            print(f"WHERE \"TransactionID\" IN ('{transaction_ids_str}')")
            print("AND \"TransactionStatus\" IN ('Transaction Pending', 'Payment Pending');")
            print()
            
            # Save detailed report to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"orphaned_products_report_{timestamp}.csv"
            df.to_csv(csv_filename, index=False)
            print(f"📄 Detailed report saved to: {csv_filename}")
            
            # Calculate financial impact
            total_value = df['Price'].sum()
            total_weight = df['Weight'].sum()
            print(f"💰 Total financial impact: ${total_value:,.2f}")
            print(f"⚖️  Total weight affected: {total_weight:,.2f} kg")
            print(f"📈 Average hours stuck: {df['Hours Since Expired'].mean():.2f} hours")
            
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        raise

def main():
    load_dotenv()
    """Main function"""
    print("🚀 Orphaned Products Detection Script")
    print(f"📅 Running at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        find_orphaned_products()
    except Exception as e:
        print(f"\n❌ Script failed with error: {str(e)}")
        sys.exit(1)
    
    print("\n✅ Script completed successfully!")

if __name__ == "__main__":
    main()