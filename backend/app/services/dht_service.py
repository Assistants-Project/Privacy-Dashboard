"""
DHT Service for publishing XACML policies to the distributed hash table.

This service handles the publication of XACML policies to the SIFIS-Home DHT,
enabling distributed policy enforcement across the smart home network.
"""

import logging
import base64
import uuid
from typing import Optional
from datetime import datetime
import requests
from ..integrations.smartotum import SmartotumClient
from ..integrations.smartotum.client import SmartotumRule


class DHTService:
    """Service for publishing policies to the DHT."""

    def __init__(self, dht_endpoint: str, rule_topic: str = "privacy_rule"):
        """Initialize DHT service.

        Args:
            dht_endpoint: DHT endpoint url
            rule_topic: The topic name for privacy rules
        """
        self.dht_endpoint = dht_endpoint
        self.rule_topic = rule_topic
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



    def publish_rule(self, topic_uuid: str, payload: dict, home_uuid: str, access_token: str) -> bool:
        """Publish a rule through Smartotum client."""
        try:
            client = SmartotumClient()
            rule = SmartotumRule(
                rule_uuid=str(topic_uuid),
                rule_topic_name=self.rule_topic,
                target_uuid=str(payload.get("target_uuid")),
                target_topic_name=str(payload.get("target_topic")),
                time_start=payload.get("time_start"),
                time_end=payload.get("time_end"),
                days=payload.get("days"),
                expiration_date=payload.get("expiration_date"),
            )
            client.post_rules(access_token, str(home_uuid), [rule])
            self.logger.info(f"Successfully published rule {topic_uuid} through Smartotum client")
            return True
        except Exception as e:
            self.logger.error(f"Error publishing rule to DHT: {e}")
            return False
        
        

    def delete_rule(self, rule_uuid: str, home_uuid: str, access_token: str) -> bool:
        """Delete a rule through Smartotum client."""
        try:
            client = SmartotumClient()
            deleted = client.delete_rule(access_token, str(home_uuid), str(rule_uuid))
            if deleted:
                self.logger.info(f"Successfully deleted rule {rule_uuid} through Smartotum client")
            else:
                self.logger.error(f"Failed to delete rule {rule_uuid} through Smartotum client")
            return deleted
        except Exception as e:
            self.logger.error(f"Error deleting rule from DHT: {e}")
            return False
