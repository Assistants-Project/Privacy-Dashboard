import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from config import BaseConfig

from ..extensions import db
from ..models.entities.sifis.db import DbRule
from ..models.entities.smart_home import SmartHome
from ..services.owl_service import OWLService
from ..services.rule_service import RuleService


class ConsentPolicyRuleService:
    """Create/delete deny rules automatically when a consent is revoked/accepted."""

    _CONSENT_RULE_NAMESPACE = UUID("7a6b7c3c-9d61-4b8e-9a1f-2fd51f2a4e6c")
    _DEFAULT_EXPIRATION_DATE = "2099/12/31"

    _owl_service_singleton: Optional[OWLService] = None

    def __init__(self, owl_service: Optional[OWLService] = None, rule_service: Optional[RuleService] = None) -> None:
        self._owl = owl_service or self._get_owl_service()
        self._rule_service = rule_service or RuleService(owl_service=self._owl)

    @classmethod
    def _get_owl_service(cls) -> OWLService:
        if cls._owl_service_singleton is not None:
            return cls._owl_service_singleton
        owl_config = {
            "ONTOLOGY_DIRECTORY": BaseConfig.ONTOLOGY_DIRECTORY,
            "ONTOLOGY_SIFIS_FILE": BaseConfig.ONTOLOGY_SIFIS_FILE,
            "LOGGING_LEVEL": BaseConfig.LOGGING_LEVEL,
        }
        cls._owl_service_singleton = OWLService(owl_config)
        return cls._owl_service_singleton

    @classmethod
    def consent_rule_uuid(cls, *, home_uuid: str, consent_uuid: UUID) -> str:
        """Deterministic base UUID for this consent in this home."""
        return str(uuid.uuid5(cls._CONSENT_RULE_NAMESPACE, f"consent:{home_uuid}:{consent_uuid}"))

    def create_consent_deny_rule(self, *, smart_home: SmartHome, subject_email: str, consent_uuid: UUID, sifis_action_id: str, access_token: str, expiration_date: Optional[str] = None) -> Tuple[int, List[str]]:
        """Create a consent-related deny rule and publish it to Smartotum DHT.

        This method does not commit the DB transaction. Caller should commit/rollback.
        Returns (db_rule_id, published_dht_rule_uuids).
        """
        expiration = (expiration_date or self._DEFAULT_EXPIRATION_DATE).replace("-", "/")
        home_uuid = str(smart_home.uuid)
        base_rule_uuid = self.consent_rule_uuid(home_uuid=home_uuid, consent_uuid=consent_uuid)

        existing = self._rule_service.rule_repo.get_rule_by_uuid(base_rule_uuid)
        if existing:
            return existing.id, []

        action_url = RuleService.SIFIS_BASE_IRI + str(sifis_action_id).strip()
        if action_url == RuleService.SIFIS_BASE_IRI:
            raise Exception("Missing sifis_action_id for consent rule creation")

        # Entire Home is represented by the home ontology location `location-home`.
        location_url = f"http://elite.polito.it/ontologies/sifis-home.owl/{home_uuid}#location-home"

        rule_data: Dict[str, Any] = {
            "effect": "deny",
            "subject": subject_email,
            "timestamp": int(time.time() * 1000),
            "expirationDate": expiration,
            "trigger": {"url": RuleService.SIFIS_ALWAYS_TRIGGER_URL, "details": []},
            "action": {
                "url": action_url,
                "details": [
                    {
                        "url": RuleService.SIFIS_LOCATION_DETAIL_URL,
                        "type": "location",
                        "value": {"name": "Entire Home", "url": location_url},
                    }
                ],
            },
        }

        timestamp = int(time.time() * 1000)
        db_rule = DbRule(
            smart_home_id=smart_home.id,
            type="sifis",
            effect="deny",
            subject=subject_email,
            timestamp=timestamp,
            rule_uuid=base_rule_uuid,
            expiration_date=expiration,
            consent_uuid=consent_uuid,
        )

        db_trigger = self._rule_service._process_trigger_data(rule_data["trigger"], smart_home)
        db_action = self._rule_service._process_action_data(rule_data["action"], smart_home)
        db_rule.triggers.append(db_trigger)
        db_rule.actions.append(db_action)

        published: List[str] = []
        try:
            self._rule_service.rule_repo.save_rule(db_rule, commit=False)

            targets = self._rule_service._targets_from_ontology(
                rule_data,
                smart_home,
                base_rule_uuid,
                location_url,
                "Entire Home",
            )
            published = self._rule_service._publish_dht_rules_for_targets(
                base_rule_uuid=base_rule_uuid,
                targets=targets,
                home_uuid=home_uuid,
                access_token=access_token,
                time_start="",
                time_end="",
                days=[],
                expiration_date=expiration,
            )
            return db_rule.id, published
        except Exception:
            # Best-effort cleanup of already published DHT rules.
            for dht_uuid in published:
                try:
                    self._rule_service.dht_service.delete_rule_strict(
                        rule_uuid=str(dht_uuid),
                        home_uuid=str(home_uuid),
                        access_token=access_token,
                    )
                except Exception:
                    pass
            raise

    def delete_consent_deny_rule(self, *, smart_home: SmartHome, consent_uuid: UUID, sifis_action_id: str, access_token: str) -> None:
        """Delete consent-related deny rule from DHT and DB.

        This method does not commit the DB transaction. Caller should commit/rollback.
        """
        home_uuid = str(smart_home.uuid)
        base_rule_uuid = self.consent_rule_uuid(home_uuid=home_uuid, consent_uuid=consent_uuid)

        action_url = RuleService.SIFIS_BASE_IRI + str(sifis_action_id).strip()
        if action_url == RuleService.SIFIS_BASE_IRI:
            raise Exception("Missing sifis_action_id for consent rule deletion")

        db_rule = self._rule_service.rule_repo.get_rule_by_uuid(base_rule_uuid)
        if db_rule:
            # Strict: if we can't delete from DHT, we must not delete from DB.
            self._rule_service._delete_dht_rule_with_fanout_support(
                db_rule, smart_home, access_token
            )
            db.session.delete(db_rule)
            db.session.flush()
