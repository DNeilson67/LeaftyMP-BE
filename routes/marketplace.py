from typing import Dict, List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from requests import Session
from fastapi.responses import JSONResponse
import crud
import models
from database import get_db
from schemas.transaction_schemas import MarketShipmentCreate, BulkTransactionCreate, BulkTransactionResponse
from schemas.transaction_schemas import TransactionDisplayBase
from schemas.user_schemas import SessionData
from schemas.flour_schemas import SimpleFlour
from schemas.leaves_schemas import SimpleDryLeaves
from routes.auth import verifier, cookie
from utils.distance import calculate_distances_from_point, sort_by_distance

router = APIRouter()

@router.post("/marketplace/create_transaction", dependencies=[Depends(cookie)])                
def create_new_transaction(market_shipment: MarketShipmentCreate, db: Session = Depends(get_db), session_data: SessionData = Depends(verifier)):
    return crud.create_single_transaction_by_customer(db=db, market_shipment=market_shipment, session_data=session_data)                     

@router.post("/marketplace/create_bulk_transaction", response_model=BulkTransactionResponse, dependencies=[Depends(cookie)])
def create_bulk_transaction(bulk_transaction: BulkTransactionCreate, db: Session = Depends(get_db), session_data: SessionData = Depends(verifier)):
    """Create a bulk transaction with multiple items from potentially different centras"""
    return crud.create_bulk_transaction_by_customer(db=db, bulk_transaction=bulk_transaction, session_data=session_data)

@router.get("/marketplace/get_transactions_by_customer", dependencies=[Depends(cookie)])
def get_marketplace_transaction_details(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: str = Query(None, description="Search by Transaction ID or Centra Username"),
    product_type: str = Query(None, description="Filter by product type: Wet Leaves, Dry Leaves, Powder"),
    transaction_status: str = Query(None, description="Filter by transaction status"),
    transaction_type: str = Query(None, description="Filter by transaction type: Single, Bulk, All"),
    session_data: SessionData = Depends(verifier),
    db: Session = Depends(get_db)
):
    """
    Get paginated transactions for the authenticated customer with filtering options
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Number of records to return (max 100)
    - **search**: Search by Transaction ID or Centra Username
    - **product_type**: Filter by product type (Wet Leaves, Dry Leaves, Powder)
    - **transaction_status**: Filter by transaction status
    - **transaction_type**: Filter by transaction type (Single, Bulk, All)
    """
    result = crud.get_transactions_by_customer(
        db=db, 
        skip=skip, 
        limit=limit, 
        session_data=session_data,
        search=search,
        product_type=product_type,
        transaction_status=transaction_status,
        transaction_type=transaction_type
    )
    
    return result

@router.get("/marketplace/get_transaction_details/{transaction_id}", response_model=TransactionDisplayBase, dependencies=[Depends(cookie)])
def get_marketplace_transaction_details(
    transaction_id: str,
    session_data: SessionData = Depends(verifier),
    db: Session = Depends(get_db)
):
    transaction = crud.get_transaction_details_by_id(db=db, transaction_id=transaction_id, session_data=session_data)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction


@router.get("/marketplace/bulkItem", dependencies=[Depends(cookie)])
def bulk_item_selection_by_items(
    item_type: str,
    target_weight: int,
    mode: str = "random",
    selected_centra_ids: Optional[List[str]] = Query(default=None),
    session_data: SessionData = Depends(verifier),
    db: Session = Depends(get_db),
):
    """
    Bulk item selection with three modes:
    - random: Random selection of centras (default)
    - closest: Sort centras by distance from user location (uses session data)
    - customized: Use only user-selected centras (requires selected_centra_ids)
    """
    try:        
        max_value = 0
        choices = {}
        centra_details = {}
        user_latitude = None
        user_longitude = None
        
        # Get user location from session data for closest mode
        if mode == "closest":
            user_location = crud.get_location_by_user_id(db, str(session_data.UserID))
            if user_location and user_location.latitude and user_location.longitude:
                user_latitude = user_location.latitude
                user_longitude = user_location.longitude
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="User location not found. Please set your location in profile settings."
                )
        
        if mode == "customized":
            # Customized mode: Use only selected centras
            if not selected_centra_ids or len(selected_centra_ids) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Customized mode requires selected_centra_ids. Please select at least one centra."
                )
            
            # Convert string IDs to UUID objects for the function
            from uuid import UUID
            centra_uuids = [UUID(cid) for cid in selected_centra_ids]
            
            max_value, choices = crud.bulk_algorithm_by_selected_centra(
                db, 
                item_type=item_type, 
                target_weight=target_weight, 
                users=centra_uuids
            )
            
        elif mode == "closest":
            # Closest mode: Sort centras by distance
            if user_latitude is None or user_longitude is None:
                raise HTTPException(
                    status_code=400,
                    detail="User location (latitude and longitude) is required for closest mode."
                )
            
            # ✅ OPTIMIZED: Get all centras with locations in ONE query using JOIN
            centras_query = (
                db.query(
                    models.User.UserID,
                    models.User.Username,
                    models.Location.latitude,
                    models.Location.longitude,
                    models.Location.location_address
                )
                .select_from(models.User)
                .join(models.Location, models.User.UserID == models.Location.user_id)
                .filter(
                    models.User.RoleID == 1,  # RoleID 1 = Centra
                    models.Location.latitude.isnot(None),
                    models.Location.longitude.isnot(None)
                )
                .all()
            )
            
            # Convert query results to list of dicts
            centras_with_locations = [
                {
                    'user_id': row.UserID,
                    'username': row.Username,
                    'latitude': row.latitude,
                    'longitude': row.longitude,
                    'location_address': row.location_address
                }
                for row in centras_query
            ]
            
            if not centras_with_locations:
                raise HTTPException(
                    status_code=400,
                    detail="No centras with valid locations found."
                )
            
            # Sort centras by distance
            sorted_centras = sort_by_distance(
                user_latitude,
                user_longitude,
                centras_with_locations,
                latitude_key='latitude',
                longitude_key='longitude'
            )
            
            # Extract just the centra data with distance info
            closest_centras = []
            for centra_data, distance in sorted_centras:
                centra_data['distance_km'] = distance
                closest_centras.append(centra_data)
            
            # Use top centras for algorithm (e.g., closest 10)
            top_centra_count = min(10, len(closest_centras))
            selected_centras = closest_centras[:top_centra_count]
            
            from uuid import UUID
            centra_uuids = [UUID(c['user_id']) for c in selected_centras]
            
            max_value, choices = crud.bulk_algorithm_by_selected_centra(
                db,
                item_type=item_type,
                target_weight=target_weight,
                users=centra_uuids
            )
            
            # Add centra details with distances (already have all data from the JOIN)
            for centra in closest_centras:
                centra_details[centra['user_id']] = {
                    'username': centra['username'],
                    'distance_km': centra['distance_km'],
                    'latitude': centra['latitude'],
                    'longitude': centra['longitude'],
                    'location_address': centra.get('location_address', '')
                }
            
        else:
            # Random mode (default): Use existing random algorithm
            max_value, choices = crud.bulk_algorithm_by_random_items(
                db, 
                item_type=item_type, 
                target_weight=target_weight
            )
        
        # If we calculated distances, add them to the response
        if centra_details:
            # Also calculate distances for centras in choices if not already done
            if mode != "closest" and user_latitude and user_longitude:
                # Get centra IDs that need location data
                missing_centra_ids = [cid for cid in choices.keys() if cid not in centra_details]
                
                if missing_centra_ids:
                    # ✅ OPTIMIZED: Fetch all missing centra data in ONE query using JOIN
                    missing_centras_query = (
                        db.query(
                            models.User.UserID,
                            models.User.Username,
                            models.Location.latitude,
                            models.Location.longitude,
                            models.Location.location_address
                        )
                        .select_from(models.User)
                        .join(models.Location, models.User.UserID == models.Location.user_id)
                        .filter(
                            models.User.UserID.in_(missing_centra_ids),
                            models.Location.latitude.isnot(None),
                            models.Location.longitude.isnot(None)
                        )
                        .all()
                    )
                    
                    # Calculate distances and add to centra_details
                    from utils.distance import calculate_distance
                    for row in missing_centras_query:
                        distance = calculate_distance(
                            user_latitude, user_longitude,
                            row.latitude, row.longitude
                        )
                        centra_details[row.UserID] = {
                            'username': row.Username,
                            'distance_km': distance,
                            'latitude': row.latitude,
                            'longitude': row.longitude,
                            'location_address': row.location_address
                        }
            
            return {
                "max_value": max_value,
                "choices": choices,
                "centra_details": centra_details,
                "mode": mode
            }
        
        return {
            "max_value": max_value,
            "choices": choices,
            "mode": mode
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing bulk algorithm: {str(e)}")