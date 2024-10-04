import requests
from pydantic import BaseModel, Field
from typing import Optional, Callable, Awaitable

class ReplicatePipeline:
    class Valves(BaseModel):
        api_key: str = Field(..., description="API key for Replicate")
        model_version: str = Field(..., description="Replicate model version to use")
        
    def __init__(self):
        self.valves = self.Valves(
            api_key="your_replicate_api_key",  # Replace with your Replicate API key
            model_version="flux-1.1-pro-model-id"  # Replace with the correct model version ID from Replicate
        )

    async def run(
        self,
        prompt: str,
        __event_emitter__: Optional[Callable[[dict], Awaitable[None]]] = None
    ) -> dict:
        """
        This method sends a request to Replicate to generate an image based on the prompt.
        """
        headers = {
            "Authorization": f"Token {self.valves.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "version": self.valves.model_version,
            "input": {
                "prompt": prompt
            }
        }

        response = requests.post("https://api.replicate.com/v1/predictions", json=data, headers=headers)

        if response.status_code == 200:
            prediction = response.json()
            image_url = prediction['urls']['get']
            return {"image_url": image_url}
        else:
            return {"error": response.text}
