from fastapi import HTTPException, status
import requests

from utils.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI


def get_google_user_details(auth_code):
    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": auth_code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        response = requests.post(token_url, data=data)
        response_data = response.json()

        if "error" in response_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Auth Code"
            )

        access_token = response_data.get("access_token")
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        user_info_res = requests.get(user_info_url, params={
                                     "access_token": access_token})
        user_info = user_info_res.json()

        return {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Auth Code"
        )
