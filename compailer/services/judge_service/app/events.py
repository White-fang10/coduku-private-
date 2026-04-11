import redis.asyncio as aioredis
from typing import Callable
import json
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class EventBus:
    """Redis-based event bus for inter-service communication"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None
        self.pubsub = None
        self.handlers: dict = {}
    
    async def init(self):
        """Initialize Redis connection"""
        self.redis = await aioredis.from_url(self.redis_url)
        self.pubsub = self.redis.pubsub()
        logger.info("✅ Event bus initialized")
    
    async def publish(self, channel: str, data: dict):
        """Publish event to channel"""
        if not self.redis:
            await self.init()
        
        message = json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        })
        
        await self.redis.publish(channel, message)
        logger.debug(f"📤 Event published: {channel}")
    
    async def subscribe(self, channel: str, handler: Callable):
        """Subscribe to channel with handler"""
        if not self.pubsub:
            await self.init()
        
        await self.pubsub.subscribe(channel)
        self.handlers[channel] = handler
        logger.info(f"📥 Subscribed to: {channel}")
        
        # Start listening
        asyncio.create_task(self._listen())
    
    async def _listen(self):
        """Listen for published events"""
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"].decode() if isinstance(message["channel"], bytes) else message["channel"]
                data = json.loads(message["data"])
                
                if channel in self.handlers:
                    await self.handlers[channel](data)
