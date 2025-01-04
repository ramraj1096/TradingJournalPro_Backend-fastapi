from fastapi import APIRouter, Depends, status, HTTPException
from datetime import datetime
from bson import ObjectId

from app.config.jwt_config import verify_token_dependency
from app.models.trade import NewTrade, ResponseModel
from ..config import collection_name_users, collection_name_trades, collection_name_journals

router = APIRouter()

@router.post("/{user_id}/new-trade/", tags=["trades"], status_code=status.HTTP_201_CREATED)
async def create_trade(user_id: str, new_trade: NewTrade, user: dict = Depends(verify_token_dependency)  ) -> ResponseModel:
    try:
        # Convert user_id to ObjectId
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

    # Check if user exists in the database
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Calculating investments
    total_traded_value = new_trade.quantity * new_trade.enter_price
    total_traded_profit = new_trade.quantity * new_trade.exit_price
    total_profit_or_loss = total_traded_profit - total_traded_value

    # If trade is a day trade, create a journal entry
    if new_trade.trade_type == "Day Trade":
        journal_data = {
            "asset_name": new_trade.asset_name,
            "quantity": new_trade.quantity,
            "asset_type": "equity",
            "journal_for": "Trade",
            "trade_category": new_trade.trade_category,
            "enter_price": new_trade.enter_price,
            "exit_price": new_trade.exit_price,
            "stop_loss": 0.00,
            "strategy_name": new_trade.strategy_name,
            "strategy_description": new_trade.strategy_description,
            "user": str(user_object_id),
            "date": datetime.now()
        }

        # Insert journal entry into the collection
        journal = collection_name_journals.insert_one(journal_data)

        # Update user by adding the journal entry ID
        collection_name_users.update_one(
            {"_id": user_object_id},
            {"$push": {"journals": str(journal.inserted_id)}}
        )

        return ResponseModel(
            success=True,
            message="Day trade journal added successfully",
            data={**journal_data, "_id": str(journal.inserted_id)}
        )

    # For new trades, prepare trade data
    trade_data = {
        "asset_name": new_trade.asset_name,
        "quantity": new_trade.quantity,
        "trade_category": new_trade.trade_category,
        "journal_for": "Trade",
        "trade_type": new_trade.trade_type,
        "enter_price": new_trade.enter_price,
        "stop_loss": 0.00,
        "exit_price": new_trade.exit_price,
        "total_traded": total_traded_value,
        "profit_or_loss": total_profit_or_loss,
        "date": new_trade.date,
        "strategy_name": new_trade.strategy_name,
        "strategy_description": new_trade.strategy_description,
        "user": str(user_object_id),
        "created_at": datetime.now()
    }

    # Insert trade into the trades collection
    trade = collection_name_trades.insert_one(trade_data)

    # Update user by adding the trade entry ID
    collection_name_users.update_one(
        {"_id": user_object_id},
        {"$push": {"trades": str(trade.inserted_id)}}
    )

    return ResponseModel(
        success=True,
        message="Trade added successfully",
        data={**trade_data, "_id": str(trade.inserted_id)}
    )

@router.get("/{user_id}/all-trades", tags=["trades"], status_code=status.HTTP_200_OK)
async def get_all_trades(user_id: str,user: dict = Depends(verify_token_dependency)  ) -> ResponseModel:
    try:
        user_object_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    # Check if the user exists in the database
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Fetch all trades for the given user
    trades_cursor = collection_name_trades.find({"user": user_id})
    trades = list(trades_cursor)

    # Convert ObjectId to string for each trade
    for trade in trades:
        trade["_id"] = str(trade["_id"])
        trade["user"] = str(trade["user"])

    return ResponseModel(
        success=True,
        message="All trades retrieved successfully",
        data=trades
    )


@router.get("/{user_id}/{trade_id}", tags=["trades"], status_code=status.HTTP_200_OK)
async def get_trade(user_id: str, trade_id: str, user: dict = Depends(verify_token_dependency)  ) -> ResponseModel:
    try:
        # Convert IDs to ObjectId
        user_object_id = ObjectId(user_id)
        trade_object_id = ObjectId(trade_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    # Check if user exists
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Query for trade with ownership verification
    trade = collection_name_trades.find_one({"_id": trade_object_id, "user": user_id})
    if not trade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade does not exist or does not belong to the user")

    # Convert ObjectId fields to string
    trade["_id"] = str(trade["_id"])
    trade["user"] = str(trade["user"])

    # Return success response
    return ResponseModel(success=True, message="Trade retrieved successfully", data=trade)



@router.put("/{user_id}/{trade_id}", tags=["trades"], status_code=status.HTTP_200_OK)
async def update_holding(user_id: str, trade_id: str, trade_data: NewTrade, user: dict = Depends(verify_token_dependency)  ) -> ResponseModel:
    try:
        user_object_id = ObjectId(user_id)
        trade_object_id = ObjectId(trade_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    # Check if user exists
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Check if trade exists and belongs to the user
    existing_trade = collection_name_trades.find_one({"_id": trade_object_id, "user": user_id})
    if not existing_trade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade does not exist or does not belong to the user")

    # Calculate updated total traded value and profit/loss
    total_traded_value = trade_data.quantity * trade_data.enter_price
    total_traded_profit = trade_data.quantity * trade_data.exit_price
    total_profit_or_loss = total_traded_profit - total_traded_value

    # Prepare updated trade data
    updated_trade_data = {
        "asset_name": trade_data.asset_name,
        "quantity": trade_data.quantity,
        "trade_category": trade_data.trade_category,
        "trade_type": trade_data.trade_type,
        "enter_price": trade_data.enter_price,
        "exit_price": trade_data.exit_price,
        "stop_loss": 0.00,
        "total_traded": total_traded_value,
        "profit_or_loss": total_profit_or_loss,
        "strategy_name": trade_data.strategy_name,
        "strategy_description": trade_data.strategy_description,
        "date": trade_data.date
    }

    # Update the trade in the collection
    result = collection_name_trades.update_one(
        {"_id": trade_object_id},
        {"$set": updated_trade_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update trade")

    return ResponseModel(
        success=True,
        message="Trade updated successfully",
        data={**updated_trade_data, "_id": trade_id}
    )


@router.delete("/{user_id}/{trade_id}", tags=["trades"], status_code=status.HTTP_200_OK)
async def delete_trade(user_id: str, trade_id: str,user: dict = Depends(verify_token_dependency)  ) -> ResponseModel:
    try:
        # Convert IDs to ObjectId
        user_object_id = ObjectId(user_id)
        trade_object_id = ObjectId(trade_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    # Check if user exists
    existing_user = collection_name_users.find_one({"_id": user_object_id})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Check if trade exists and belongs to the user
    existing_trade = collection_name_trades.find_one({"_id": trade_object_id, "user": user_id})
    if not existing_trade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade does not exist or does not belong to the user")
    
    # Prepare journal data for deletion record
    journal_data = {
        "asset_name": existing_trade["asset_name"],
        "quantity": existing_trade["quantity"],
        "asset_type": existing_trade.get("asset_type", "unknown"),
        "journal_for": "Deleted Trade",
        "trade_category": "sell",
        "enter_price": existing_trade["enter_price"],
        "exit_price": existing_trade["exit_price"],
        "stop_loss": existing_trade.get("stop_loss", 0.00),
        "strategy_name": existing_trade["strategy_name"],
        "strategy_description": existing_trade["strategy_description"],
        "date": datetime.now(),
        "user": str(user_object_id),
    }

    try:
        # Insert journal entry for deletion record
        journal = collection_name_journals.insert_one(journal_data)

        # Delete trade and update user data
        collection_name_trades.delete_one({"_id": trade_object_id})
        collection_name_users.update_one(
            {"_id": user_object_id},
            {
                "$pull": {"trades": str(trade_object_id)},
                "$push": {"journals": str(journal.inserted_id)}
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete trade: {str(e)}")

    # Return success response
    return ResponseModel(success=True, message="Trade deleted successfully", data={})
