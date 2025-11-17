"""
DHT Service for publishing XACML policies to the distributed hash table.

This service handles the publication of XACML policies to the SIFIS-Home DHT,
enabling distributed policy enforcement across the smart home network.
"""

import logging
import json
import base64
import uuid
from typing import Optional
from datetime import datetime
import requests


class DHTService:
    """Service for publishing policies to the DHT."""

    def __init__(self, dht_endpoint: str = "http://host.docker.internal:3000/"):
        """Initialize DHT service.

        Args:
            dht_endpoint: DHT endpoint url
        """
        self.dht_endpoint = dht_endpoint
        self.logger = logging.getLogger(__name__)

    def publish_policy(self, policy_xml: str, policy_id: str) -> Optional[str]:
        """Publish a policy to the DHT.

        Args:
            policy_xml: XML string of the policy
            policy_id: Policy identifier

        Returns:
            Response from DHT or None if failed
        """
        try:
            # Encode policy to base64
            policy_base64 = base64.b64encode(policy_xml.encode("utf-8")).decode("utf-8")

            timestamp = int(datetime.now().timestamp() * 1000)

            # Create message structure following Java implementation
            message = {
                "purpose": "ADD_POLICY",
                "message_id": str(uuid.uuid4()),
                "policy": policy_base64,
                "policy_id": policy_id,
            }

            message_ext = {
                "message": message,
                "id": f"pap-{uuid.uuid4()}",
                "topic_name": "topic-name",
                "topic_uuid": "topic-uuid-the-ucs-is-subscribed-to",
            }

            command = {"command_type": "pap-command", "value": message_ext}

            value = {"timestamp": timestamp, "command": command}

            # Send to DHT
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.dht_endpoint}pub", json=value, headers=headers, timeout=10
            )

            if response.status_code == 200:
                self.logger.info(f"Successfully published policy {policy_id} to DHT")
                return response.text
            else:
                self.logger.error(
                    f"Failed to publish policy {policy_id}: {response.status_code}"
                )
                return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error publishing policy to DHT: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error publishing policy: {e}")
            return None
