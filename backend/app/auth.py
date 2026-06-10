from fastapi import Header, HTTPException, Security, status
from app import config

async def verify_api_key(x_api_key: str = Header(None)):
    expected_key = config.PROMPT_LOG_API_KEY
    
    # If API Key is not configured in .env, skip authentication
    if not expected_key:
        return None
        
    # If API Key is configured, it must match the X-API-Key header
    if x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header"
        )
    return x_api_key
