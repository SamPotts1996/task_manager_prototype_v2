import logging
from typing import Dict, List, Callable, Any
import time
import uuid
from queue import Queue, Empty
from threading import Thread, Event

logger = logging.getLogger(__name__)

class Message:
    def __init__(self, topic: str, data: Any):
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.data = data
        self.timestamp = time.time()

class MessageBroker:
    def __init__(self):
        self.topics: Dict[str, Queue] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self.running = True
        self.processing_threads = {}
        self._stop_event = Event()

    def create_topic(self, topic: str):
        if topic not in self.topics:
            self.topics[topic] = Queue()
            self.subscribers[topic] = []
            self._start_topic_processor(topic)
            logger.debug(f"[MessageBroker] Created topic: {topic}")

    def publish(self, topic: str, message: Any):
        if topic not in self.topics:
            self.create_topic(topic)
        msg = Message(topic, message)
        self.topics[topic].put(msg)
        logger.debug(f"[MessageBroker] Published message to topic {topic}: {message}")

    def subscribe(self, topic: str, callback: Callable):
        if topic not in self.subscribers:
            self.create_topic(topic)
        self.subscribers[topic].append(callback)
        logger.debug(f"[MessageBroker] Subscribed callback to topic {topic}")

    def _start_topic_processor(self, topic: str):
        def process_topic():
            while not self._stop_event.is_set():
                try:
                    msg = self.topics[topic].get(timeout=1)
                    for callback in self.subscribers[topic]:
                        try:
                            callback(msg.data)
                        except Exception as e:
                            logger.exception(f"Error in subscriber callback: {e}")
                except Empty:
                    continue

        thread = Thread(target=process_topic, daemon=True)
        thread.start()
        self.processing_threads[topic] = thread

    def stop(self):
        logger.info("[MessageBroker] Stopping...")
        self._stop_event.set()
        for thread in self.processing_threads.values():
            thread.join()
        self.running = False
