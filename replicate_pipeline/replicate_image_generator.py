import requests
from pydantic import BaseModel, Field
from typing import Optional, Callable, Awaitable, Any

# Define the pipeline for connecting to Replicate API
class ReplicateImageGenerator:
    class Config(BaseModel):
        replicate_model: str = Field(
            default="black-forest-labs/flux-1.1-pro", 
            description="The model ID from Replicate to use for image generation"
        )
        api_url: str = Field(
            default="https://api.replicate.com/v1/predictions", 
            description="Base URL for the Replicate API"
        )
        api_token: str = Field(
            default="", 
            description="Your Replicate API token"
        )

    def __init__(self):
        self.config = self.Config(api_token="<YOUR_API_KEY>")  # You will replace this in UI

    async def generate_image(self, prompt: str, __event_emitter__: Optional[Callable[[dict], Awaitable[None]]] = None) -> str:
        # Prepare request data
        headers = {
            "Authorization": f"Token {self.config.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "version": self.config.replicate_model,
            "input": {
                "prompt": prompt
            }
        }

        # Call Replicate API
        response = requests.post(self.config.api_url, json=payload, headers=headers)
        
        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"

        result = response.json()
        prediction_id = result["id"]

        # Poll for the prediction result
        status_url = f"{self.config.api_url}/{prediction_id}"
        while True:
            poll_response = requests.get(status_url, headers=headers)
            poll_result = poll_response.json()

            if poll_result['status'] == 'succeeded':
                return poll_result['output'][0]
            elif poll_result['status'] == 'failed':
                return "Error: Image generation failed."
            
            # Emit status (if the UI supports this feature)
            if __event_emitter__:
                await __event_emitter__({"status": f"Image generation in progress... {poll_result['status']}"})

        return "Error: Unexpected status in image generation."

# Entry function to handle the request and return the image URL
async def pipeline(body: dict, __user__: Optional[dict] = None, __event_emitter__: Optional[Callable[[dict], Awaitable[None]]] = None) -> dict:
    generator = ReplicateImageGenerator()
    prompt = body.get("prompt", "A beautiful landscape")  # Default prompt
    image_url = await generator.generate_image(prompt, __event_emitter__)

    return {
        "prompt": prompt,
        "image_url": image_url
    }

