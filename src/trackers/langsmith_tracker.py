from langsmith import Client
from datetime import datetime
from typing import Dict, Any

class LangSmithTracker:
    def __init__(self, api_key: str):
        self.client = Client(api_key=api_key)
        
    def track_generation(self, prompt: str, completion: str, metadata: Dict[Any, Any]):
        run = self.client.create_run(
            name="content_generation",
            inputs={"prompt": prompt},
            outputs={"completion": completion},
            timestamps={
                "start_time": datetime.utcnow().isoformat(),
                "end_time": datetime.utcnow().isoformat()
            },
            metadata=metadata
        )
        return run.id