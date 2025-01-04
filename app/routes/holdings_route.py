from fastapi import APIRouter, Depends, status, HTTPException
from datetime import datetime
from bson import ObjectId

from app.models.holding import NewHolding, ResponseModel, UpdateHolding
from ..config import collection_name_users, collection_name_holdings, collection_name_journals
from app.config.jwt_config import verify_token_dependency

router = APIRouter()

@router.post("/{user_id}/new-holding/", tags=["holdings"], status_code=status.HTTP_201_CREATED)
async def create_holding(
    user_id: str, 
    new_holding: NewHolding, 
    user: dict = Depends(verify_token_dependency)  
) -> ResponseModel:
    try:
        # Convert user_id to ObjectId
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

    # Check if user exists in the database
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Calculate investments
    total_investment = new_holding.quantity * new_holding.bought_price
    current_investment = new_holding.quantity * new_holding.current_price

    # Prepare holding data
    holding_data = {
        "asset_name": new_holding.asset_name,
        "quantity": new_holding.quantity,
        "bought_price": new_holding.bought_price,
        "current_price": new_holding.current_price,
        "total_investment": total_investment,
        "current_investment": current_investment,
        "date": new_holding.date,
        "user": str(user_object_id),
        "created_at": datetime.now()
    }

    # Prepare journal data
    journal_data = {
        "asset_name": new_holding.asset_name,
        "quantity": new_holding.quantity,
        "asset_type": "equity",
        "journal_for": "Holding",
        "trade_category": "buy",
        "enter_price": new_holding.bought_price,
        "exit_price": new_holding.current_price,
        "stop_loss": 0.00,
        "strategy_name": "Longterm",
        "strategy_description": "Longterm",
        "user": str(user_object_id),
        "date": datetime.now()
    }

    try:
        # Insert journal data
        journal = collection_name_journals.insert_one(journal_data)

        # Insert holding data
        result = collection_name_holdings.insert_one(holding_data)

        # Update user with new holding and journal
        collection_name_users.update_one(
            {"_id": user_object_id},
            {
                "$push": {
                    "holdings": str(result.inserted_id),
                    "journals": str(journal.inserted_id)
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Return success response
    return ResponseModel(
        success=True,
        message="Holding added successfully",
        data={**holding_data, "_id": str(result.inserted_id)}
    )

@router.get("/{user_id}/all-holdings", 
            tags=["holdings"], 
            status_code=status.HTTP_200_OK)
async def get_all_holdings(user_id: str,user: dict = Depends(verify_token_dependency)) -> ResponseModel:
    try:
        user_object_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    holdings_ids = existing_user.get("holdings", [])
    holdings_data = list(collection_name_holdings.find({"_id": {"$in": [ObjectId(h) for h in holdings_ids]}}))
    for holding in holdings_data:
        holding["_id"] = str(holding["_id"])
        holding["user"] = str(holding["user"])

    return ResponseModel(success=True, message="Holdings retrieved successfully", data=holdings_data)


@router.get("/{user_id}/{holding_id}", tags=["holdings"], status_code=status.HTTP_200_OK)
async def get_holding(user_id: str, holding_id: str,user: dict = Depends(verify_token_dependency)) -> ResponseModel:
    try:
        user_object_id = ObjectId(user_id)
        holding_object_id = ObjectId(holding_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    holding = collection_name_holdings.find_one({"_id": holding_object_id})

    if not holding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding does not exist or does not belong to the user")

    holding["_id"] = str(holding["_id"])
    holding["user"] = str(holding["user"])

    return ResponseModel(success=True, message="Holding retrieved successfully", data=holding)



@router.put("/{user_id}/{holding_id}", tags=["holdings"], status_code=status.HTTP_200_OK)
async def update_holding(user_id: str, holding_id: str, holding_data: UpdateHolding, user: dict = Depends(verify_token_dependency)  ) -> ResponseModel:
    try:
        user_object_id = ObjectId(user_id)
        holding_object_id = ObjectId(holding_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    existing_holding = collection_name_holdings.find_one({"_id": holding_object_id})
    if not existing_holding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding does not exist or does not belong to the user")

    updated_quantity = holding_data.quantity if holding_data.quantity is not None else existing_holding["quantity"]
    updated_bought_price = holding_data.bought_price if holding_data.bought_price is not None else existing_holding["bought_price"]
    updated_current_price = holding_data.current_price if holding_data.current_price is not None else existing_holding["current_price"]

    total_investment = updated_quantity * updated_bought_price
    current_investment = updated_quantity * updated_current_price

    update_fields = {
        "asset_name": holding_data.asset_name if holding_data.asset_name is not None else existing_holding["asset_name"],
        "quantity": updated_quantity,
        "bought_price": updated_bought_price,
        "current_price": updated_current_price,
        "total_investment": total_investment,
        "current_investment": current_investment,
        "date": holding_data.date if holding_data.date is not None else existing_holding["date"],
        "updated_at": datetime.now()
    }

    collection_name_holdings.update_one({"_id": holding_object_id}, {"$set": update_fields})
    updated_holding = collection_name_holdings.find_one({"_id": holding_object_id})
    updated_holding["_id"] = str(updated_holding["_id"])
    updated_holding["user"] = str(updated_holding["user"])

    return ResponseModel(success=True, message="Holding updated successfully", data=updated_holding)


@router.delete("/{user_id}/{holding_id}", tags=["holdings"], status_code=status.HTTP_200_OK)
async def delete_holding(user_id: str, holding_id: str, user: dict = Depends(verify_token_dependency)  ) -> ResponseModel:
    try:
        # Convert IDs to ObjectId
        user_object_id = ObjectId(user_id)
        holding_object_id = ObjectId(holding_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    # Check if user exists
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Check if holding exists and belongs to the user
    existing_holding = collection_name_holdings.find_one({"_id": holding_object_id})
    if not existing_holding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding does not exist or does not belong to the user")

    # Prepare journal data for deletion record
    journal_data = {
        "asset_name": existing_holding["asset_name"],
        "quantity": existing_holding["quantity"],
        "asset_type": "equity",
        "journal_for": "Holding",
        "trade_category": "sell",
        "enter_price": existing_holding["bought_price"],
        "exit_price": existing_holding["current_price"],
        "stop_loss": 0.00,
        "strategy_name": "Longterm",
        "strategy_description": "Longterm",
        "date": datetime.now(),
        "user": str(user_object_id),
    }

    try:
        # Insert journal entry for deletion record
        journal = collection_name_journals.insert_one(journal_data)

        # Delete holding and update user data
        collection_name_holdings.delete_one({"_id": holding_object_id})
        collection_name_users.update_one(
            {"_id": user_object_id},
            {
                "$pull": {"holdings": str(holding_object_id)},
                "$push": {"journals": str(journal.inserted_id)}
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Return success response
    return ResponseModel(success=True, message="Holding deleted successfully", data={})
