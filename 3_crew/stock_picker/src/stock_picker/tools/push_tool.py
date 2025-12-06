from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests


class PushNotification(BaseModel):
    """A message to be sent to the user"""
    message: str = Field(..., description="The message to be sent to the user.")

class PushNotificationTool(BaseTool):
    
    name: str = "send_push_notification"
    description: str = (
        "Use this tool to send a push notification message to the user. "
        "Call this tool when you need to notify the user about your decision or important findings. "
        "Required parameter: message (string) - the notification message to send."
    )
    args_schema: Type[BaseModel] = PushNotification

    def _run(self, message: str) -> str:
        """Execute the push notification tool"""
        # Clear logging to verify tool execution
        print("\n" + "🔔" * 30)
        print("PUSH NOTIFICATION TOOL EXECUTED!")
        print("🔔" * 30)
        print(f"Message: {message}")
        print("🔔" * 30 + "\n")
        
        # pushover_user = os.getenv("PUSHOVER_USER")
        # pushover_token = os.getenv("PUSHOVER_TOKEN")
        # pushover_url = "https://api.pushover.net/1/messages.json"

        # payload = {"user": pushover_user, "token": pushover_token, "message": message}
        # requests.post(pushover_url, data=payload)
        return '{"notification": "ok"}'