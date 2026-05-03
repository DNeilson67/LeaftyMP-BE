from typing import Dict, List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from requests import Session
from fastapi.responses import JSONResponse
from routes.auth import verifier, cookie
import crud
from database import get_db
from schemas.user_schemas import SessionData
from schemas.misc_schemas import BulkItemSelectionRequest
from schemas.flour_schemas import SimpleFlour
from schemas.leaves_schemas import SimpleDryLeaves
from utils.distance import calculate_distances_from_point, sort_by_distance

router = APIRouter()


@router.post("/algorithm/bulkSelectedCentra", response_model=Dict[str, Union[int, Dict[str, List[Union[SimpleFlour, SimpleDryLeaves]]]]])
def bulk_item_selection_by_selected_centras(request: BulkItemSelectionRequest, db: Session = Depends(get_db)):
    try:
        max_value, choices = crud.bulk_algorithm_by_selected_centra(
            db, 
            item_type=request.item_type, 
            target_weight=request.target_weight, 
            users=request.users
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"max_value": max_value, "choices": choices}


@router.get("/algorithm/bulkItem", dependencies=[Depends(cookie)])
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
            
            # Get all centras with locations
            all_centras = crud.get_user_by_role(db, RoleID=1)  # RoleID 1 = Centra
            centras_with_locations = []
            
            for centra in all_centras:
                location = crud.get_location_by_user_id(db, centra.UserID)
                if location and location.latitude and location.longitude:
                    centras_with_locations.append({
                        'user_id': centra.UserID,
                        'username': centra.Username,
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'location_address': location.location_address
                    })
            
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
            
            # Add centra details with distances
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
                for centra_id in choices.keys():
                    if centra_id not in centra_details:
                        centra = crud.get_user_by_id(db, centra_id)
                        location = crud.get_location_by_user_id(db, centra_id)
                        if centra and location:
                            from utils.distance import calculate_distance
                            distance = calculate_distance(
                                user_latitude, user_longitude,
                                location.latitude, location.longitude
                            )
                            centra_details[centra_id] = {
                                'username': centra.Username,
                                'distance_km': distance,
                                'latitude': location.latitude,
                                'longitude': location.longitude,
                                'location_address': location.location_address
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

    