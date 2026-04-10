from nba_api.stats.endpoints import playbyplayv3
import time
import json
import os
from kafka import KafkaProducer, KafkaConsumer
from logging import getLogger
logger = getLogger(__name__)

class KafkaProducerService:
    def __init__(self, game_id: str):
        self.game_id = game_id
        # Make bootstrap_servers configurable; default to localhost:9094 (host-facing listener)
        bootstrap = os.getenv("KAFKA_BOOTSTRAP", "localhost:9094")
        self.producer = KafkaProducer(bootstrap_servers=bootstrap)
        self.header = {
            "Accept": "application/json, text/plain, /",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "stats.nba.com",
            "Origin": "https://www.nba.com",
            "Pragma": "no-cache",
            "Referer": "https://www.nba.com/",
            "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
            ),
        }

    def produce_play_by_play(self):
        print(f"Producing message for game {self.game_id}")
        play_by_play_dict = playbyplayv3.PlayByPlayV3(game_id=self.game_id, headers=self.header).get_dict()["game"]["actions"]
        for action in play_by_play_dict:
            actions_key = ["actionId", "period", "personId", "teamId", "scoreHome", "scoreAway", "actionType"]
            cleaned = {k: action[k] for k in action if k in actions_key}
            time.sleep(1)  # Simulate delay in producing messages
            # Kafka expects bytes-like keys/values. Encode the key and send JSON bytes for the value.
            print(f"Producing message for game {self.game_id}: {cleaned}")
            future = self.producer.send(
                "nba.play_by_play.raw",
                key=self.game_id.encode("utf-8"),
                value=json.dumps(cleaned).encode("utf-8"),
            )
            # Block briefly to surface connection or delivery errors (will raise on failure)
            try:
                meta = future.get(timeout=10)
                print(f"Produced message for game {self.game_id}: {cleaned} -> {meta.topic}:{meta.partition}@{meta.offset}")
            except Exception as exc:
                print(f"Failed to send message for game {self.game_id}: {exc}")
                # flush to ensure we don't silently drop buffered messages
                try:
                    self.producer.flush(timeout=5)
                except Exception:
                    pass
                raise
        # ensure all messages are sent before exiting
        try:
            self.producer.flush(timeout=10)
        except Exception:
            pass

KafkaProducerService(game_id="0022200001").produce_play_by_play()
