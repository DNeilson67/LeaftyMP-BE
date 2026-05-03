from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException, Body
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas.location_schemas import Location, LocationCreate, LocationPatch, BatchLocationRequest
import schemas
from BasicVerifier import BasicVerifier
import requests
import time

router = APIRouter()

# Rate limiting for Nominatim API
last_nominatim_request_time = 0
NOMINATIM_RATE_LIMIT = 1.0  # 1 second between requests

@router.get('/geocode/search', tags=["Location"])
async def search_geocode(q: str, limit: int = 10):
    """
    Proxy endpoint for forward geocoding (search) to avoid CORS issues
    """
    global last_nominatim_request_time
    
    try:
        # Respect Nominatim rate limiting
        current_time = time.time()
        time_since_last_request = current_time - last_nominatim_request_time
        if time_since_last_request < NOMINATIM_RATE_LIMIT:
            time.sleep(NOMINATIM_RATE_LIMIT - time_since_last_request)
        
        last_nominatim_request_time = time.time()
        
        # Make request to Nominatim API
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'q': q,
                'format': 'json',
                'addressdetails': 1,
                'limit': limit,
                'countrycodes': 'id',
                'accept-language': 'id,en',
                'bounded': 1,
                'dedupe': 1
            },
            headers={
                'User-Agent': 'Leafty-App/1.0'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Geocoding service unavailable")
    
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Geocoding service timeout")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Geocoding service error: {str(e)}")

@router.get('/geocode/reverse', tags=["Location"])
async def reverse_geocode(lat: float, lon: float):
    """
    Proxy endpoint for reverse geocoding to avoid CORS issues
    """
    global last_nominatim_request_time
    
    try:
        # Respect Nominatim rate limiting
        current_time = time.time()
        time_since_last_request = current_time - last_nominatim_request_time
        if time_since_last_request < NOMINATIM_RATE_LIMIT:
            time.sleep(NOMINATIM_RATE_LIMIT - time_since_last_request)
        
        last_nominatim_request_time = time.time()
        
        # Make request to Nominatim API
        response = requests.get(
            'https://nominatim.openstreetmap.org/reverse',
            params={
                'format': 'json',
                'lat': lat,
                'lon': lon,
                'addressdetails': 1,
                'accept-language': 'en'
            },
            headers={
                'User-Agent': 'Leafty-App/1.0'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Geocoding service unavailable")
    
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Geocoding service timeout")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Geocoding service error: {str(e)}")

@router.post('/location/post', tags=["Location"])
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    crud.create_location(db, location=location)
    return {"code":"200"}

@router.get('/location/get', response_model=List[Location], tags=["Location"])
def get_location(limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_location(db=db, limit=limit)

@router.get('/location/getuserid/{user_id}', response_model=Location, tags=["Location"])
def get_location_by_user_id(user_id: str, db: Session = Depends(get_db)):
    location = crud.get_location_by_user_id(db=db, user_id=user_id)
    if not location:
        raise HTTPException(status_code=404, detail="location not found")
    return location

@router.patch("/location/patchuserid/{user_id}")
def patch_location_by_user_id(location: LocationPatch, user_id:str, db: Session=Depends(get_db)):
    location = crud.patch_location_by_user_id(db=db, user_id=user_id, location=location)
    return location

# New endpoint: Get authenticated user's location
@router.get('/location/user', response_model=Location, tags=["Location"])
def get_authenticated_user_location(
    session_data: schemas.SessionData,
    db: Session = Depends(get_db),
   
):
    """Get the current authenticated user's location"""
    location = crud.get_location_by_user_id(db=db, user_id=str(session_data.UserID))
    if not location:
        raise HTTPException(
            status_code=404, 
            detail="Location not found. Please set your location in profile settings."
        )
    return location

# New endpoint: Update authenticated user's location
@router.patch("/location/user", response_model=Location, tags=["Location"])
def update_authenticated_user_location(
    session_data: schemas.SessionData,
    location_update: LocationPatch,
    db: Session = Depends(get_db),
):
    """Update the current authenticated user's location"""
    updated_location = crud.patch_location_by_user_id(
        db=db, 
        user_id=str(session_data.UserID), 
        location=location_update
    )
    if not updated_location:
        raise HTTPException(status_code=404, detail="Failed to update location")
    return updated_location

# New endpoint: Get all centra locations for map display
@router.get("/location/centras", tags=["Location"])
def get_all_centra_locations(db: Session = Depends(get_db)):
    """
    Get all centra locations with their coordinates for map display.
    Returns a list of centras with their location details.
    """
    try:
        # Get all users with Centra role (RoleID = 1)
        centras = crud.get_user_by_role(db, RoleID=1)
        
        centra_locations = []
        for centra in centras:
            location = crud.get_location_by_user_id(db, centra.UserID)
            if location and location.latitude and location.longitude:
                centra_locations.append({
                    "centra_id": centra.UserID,
                    "username": centra.Username,
                    "email": centra.Email,
                    "phone_number": centra.PhoneNumber,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "location_address": location.location_address
                })
        
        return {
            "count": len(centra_locations),
            "centras": centra_locations
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching centra locations: {str(e)}"
        )

# New endpoint: Get centra locations with distance from a point
@router.get("/location/centras/nearby", tags=["Location"])
def get_nearby_centra_locations(
    latitude: float,
    longitude: float,
    max_distance_km: float = None,
    limit: int = None,
    db: Session = Depends(get_db)
):
    """
    Get centra locations sorted by distance from a given point.
    Optionally filter by maximum distance and limit results.
    """
    try:
        from utils.distance import sort_by_distance
        
        # Get all centras with locations
        centras = crud.get_user_by_role(db, RoleID=1)
        
        centras_with_locations = []
        for centra in centras:
            location = crud.get_location_by_user_id(db, centra.UserID)
            if location and location.latitude and location.longitude:
                centras_with_locations.append({
                    "centra_id": centra.UserID,
                    "username": centra.Username,
                    "email": centra.Email,
                    "phone_number": centra.PhoneNumber,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "location_address": location.location_address
                })
        
        # Sort by distance
        sorted_centras = sort_by_distance(
            latitude,
            longitude,
            centras_with_locations,
            latitude_key='latitude',
            longitude_key='longitude'
        )
        
        # Build response with distances
        result_centras = []
        for centra_data, distance in sorted_centras:
            # Filter by max distance if specified
            if max_distance_km is not None and distance > max_distance_km:
                continue
            
            centra_with_distance = centra_data.copy()
            centra_with_distance['distance_km'] = distance
            result_centras.append(centra_with_distance)
            
            # Limit results if specified
            if limit is not None and len(result_centras) >= limit:
                break
        
        return {
            "origin": {
                "latitude": latitude,
                "longitude": longitude
            },
            "count": len(result_centras),
            "centras": result_centras
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching nearby centras: {str(e)}"
        )

# New endpoint: Get multiple centra locations by IDs with distances
@router.post("/location/centras/batch", tags=["Location"])
def get_batch_centra_locations(
    request: BatchLocationRequest,
    db: Session = Depends(get_db)
):
    """
    Get locations for multiple centras by their IDs and calculate distances.
    This avoids N+1 queries by fetching all locations in a single operation.
    """
    try:
        from utils.distance import calculate_distance
        
        # Fetch all centra locations in a single query using SQL IN clause
        # This is much more efficient than making separate queries for each centra
        from sqlalchemy import and_
        from models import Location, User
        
        # Join User and Location tables to get all data in one query
        results = db.query(User, Location).join(
            Location, 
            User.UserID == Location.user_id
        ).filter(
            and_(
                User.UserID.in_(request.centra_ids),
                User.RoleID == 1,  # Ensure they are centras
                Location.latitude.isnot(None),
                Location.longitude.isnot(None)
            )
        ).all()
        
        # Build response with distances
        centra_locations = []
        for user, location in results:
            distance = calculate_distance(
                request.user_latitude,
                request.user_longitude,
                location.latitude,
                location.longitude
            )
            
            centra_locations.append({
                "centra_id": str(user.UserID),
                "username": user.Username,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "location_address": location.location_address,
                "distance_km": distance
            })
        
        return {
            "count": len(centra_locations),
            "centras": centra_locations
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching batch centra locations: {str(e)}"
        )
    
# @router.delete('/location/delete/{location_id}', tags=["Location"])
# def delete_location_by_id(location_id: int, db: Session = Depends(get_db)):
#     delete = crud.delete_location_by_id(db=db, location_id=location_id)
#     if delete:
#         return {"message": "location deleted successfully"}
#     else:
#         return {"message": "location not found or deletion failed"}
    
