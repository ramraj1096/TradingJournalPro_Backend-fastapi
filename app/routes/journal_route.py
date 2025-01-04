from fastapi import APIRouter, Depends, status, HTTPException
from datetime import datetime
from bson import ObjectId

from app.config.jwt_config import verify_token_dependency
from app.models.journal import NewJournal, ResponseModel

from ..config import collection_name_users, collection_name_journals

router = APIRouter()

@router.post("/{user_id}/new-journal/", tags=["journals"], status_code=status.HTTP_201_CREATED)
async def create_journal(user_id: str, new_journal: NewJournal, user: dict = Depends(verify_token_dependency)  ) -> ResponseModel:
    try:
        # Convert user_id to ObjectId
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

    # Check if user exists
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Prepare journal data
    journal_data = {
        "asset_name": new_journal.asset_name,
        "quantity": new_journal.quantity,
        "asset_type": new_journal.asset_type,
        "journal_for": new_journal.journal_for,
        "trade_category": new_journal.trade_category,
        "enter_price": new_journal.enter_price,
        "exit_price": new_journal.exit_price,
        "stop_loss": new_journal.stop_loss,
        "strategy_name": new_journal.strategy_name,
        "strategy_description": new_journal.strategy_description,
        "user": str(user_object_id),
        "date": datetime.now()
    }

    # Insert journal entry
    journal = collection_name_journals.insert_one(journal_data)

    # Update user's journal list
    collection_name_users.update_one(
        {"_id": user_object_id},
        {"$push": {"journals": str(journal.inserted_id)}}
    )

    # Return success response
    return ResponseModel(
        success=True,
        message="Journal added successfully",
        data={**journal_data, "_id": str(journal.inserted_id)}
    )


@router.get("/{user_id}/all-journals", tags=["journals"], status_code=status.HTTP_200_OK)
async def get_all_journals(user_id: str, user: dict = Depends(verify_token_dependency)  ) -> ResponseModel:
    try:
        # Convert user_id to ObjectId
        user_object_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    # Check if user exists
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Retrieve all journals for the user
    journals = list(collection_name_journals.find({"user": str(user_object_id)}))

    # Convert ObjectId fields to strings for proper JSON serialization
    for journal in journals:
        journal["_id"] = str(journal["_id"])
        journal["user"] = str(journal["user"])

    # Return success response with journal list
    return ResponseModel(
        success=True,
        message="All journals retrieved successfully",
        data=journals
    )


@router.get("/{user_id}/{journal_id}", tags=["journals"], status_code=status.HTTP_200_OK)
async def get_journal(user_id: str, journal_id: str, user: dict = Depends(verify_token_dependency)  ) -> ResponseModel:
    try:
        # Convert IDs to ObjectId
        user_object_id = ObjectId(user_id)
        journal_object_id = ObjectId(journal_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    # Check if user exists
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Retrieve the specific journal
    journal = collection_name_journals.find_one({"_id": journal_object_id, "user": str(user_object_id)})
    if not journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal does not exist or does not belong to the user")

    # Convert ObjectId fields to strings for proper JSON serialization
    journal["_id"] = str(journal["_id"])
    journal["user"] = str(journal["user"])

    # Return success response with the journal data
    return ResponseModel(
        success=True,
        message="Journal retrieved successfully",
        data=journal
    )



@router.put("/{user_id}/{journal_id}", tags=["journals"], status_code=status.HTTP_200_OK)
async def update_journal(user_id: str, journal_id: str, journal_data: NewJournal, user: dict = Depends(verify_token_dependency)) -> ResponseModel:
    try:
        # Convert IDs to ObjectId
        user_object_id = ObjectId(user_id)
        journal_object_id = ObjectId(journal_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    # Check if user exists
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Check if journal exists and belongs to the user
    existing_journal = collection_name_journals.find_one({"_id": journal_object_id, "user": str(user_object_id)})
    if not existing_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal does not exist or does not belong to the user")

    # Prepare updated journal data
    updated_journal_data = {
        "asset_name": journal_data.asset_name,
        "quantity": journal_data.quantity,
        "asset_type": journal_data.asset_type,
        "journal_for": journal_data.journal_for,
        "trade_category": journal_data.trade_category,
        "enter_price": journal_data.enter_price,
        "exit_price": journal_data.exit_price,
        "stop_loss": journal_data.stop_loss,
        "strategy_name": journal_data.strategy_name,
        "strategy_description": journal_data.strategy_description,
        "date": journal_data.date, 
        "user": str(user_object_id)
    }

    # Update the journal in the database
    try:
        collection_name_journals.update_one(
            {"_id": journal_object_id},
            {"$set": updated_journal_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Return success response with updated data
    return ResponseModel(
        success=True,
        message="Journal updated successfully",
        data={**updated_journal_data, "_id": str(journal_object_id)}
    )


@router.delete("/{user_id}/{journal_id}", tags=["journals"], status_code=status.HTTP_200_OK)
async def delete_journal(user_id: str, journal_id: str,user: dict = Depends(verify_token_dependency)) -> ResponseModel:
    # Ensure that the IDs are valid ObjectId format
    try:
        user_object_id = ObjectId(user_id)
        journal_object_id = ObjectId(journal_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    # Check if user exists
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Check if the journal exists and belongs to the user
    existing_journal = collection_name_journals.find_one({"_id": journal_object_id})
    if not existing_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal does not exist or does not belong to the user")

    try:
        # Delete the journal entry
        collection_name_journals.delete_one({"_id": journal_object_id})
        
        # Update the user's data to remove the journal reference
        collection_name_users.update_one(
            {"_id": user_object_id},
            {"$pull": {"journals": str(journal_object_id)}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Return success response
    return ResponseModel(success=True, message="Journal deleted successfully", data={})