# app.py
from flask import jsonify, request, send_file
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from io import BytesIO
import zipfile
import os
import shutil
import yaml
from pathlib import Path

from ..services import OWLService, XACMLService, DHTService
from ..services.rule_service import RuleService
from ..repositories.user_repository import UserRepository
from ..schemas.request.rule_req_schema import RuleRequestSchema
from marshmallow import ValidationError

import logging

sifis_bp = Blueprint(
    "SIFIS API",
    "sifis_bp",
    url_prefix="/api/sifis",
    description="Endpoints for SIFIS",
)

# Load configuration
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except Exception as e:
    logging.error(f"Failed to load config: {e}")
    config = {
        "dht": {"endpoint": "http://host.docker.internal:3000/"},
        "policies": {"directory": "data/policies/"},
    }

# Initialize Services
try:
    owl_service = OWLService()
    xacml_service = XACMLService(owl_service)
    dht_service = DHTService(config["dht"]["endpoint"])
    rule_service = RuleService(owl_service)
    user_repo = UserRepository()
    logging.info("Services initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize services: {e}")
    owl_service = None
    xacml_service = None
    dht_service = None
    rule_service = None


@sifis_bp.route("/trigger-services", methods=["GET"])
def get_trigger_services():
    """Get all services that offer triggers"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        services = owl_service.get_trigger_services()
        return jsonify([service.to_dict() for service in services])
    except Exception as e:
        logging.error(f"Error getting trigger services: {e}")
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/trigger-services/<service_id>/triggers", methods=["GET"])
def get_triggers(service_id):
    """Get triggers for a specific service"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        triggers = owl_service.get_triggers(service_id)
        return jsonify([trigger.to_dict() for trigger in triggers])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sifis_bp.route(
    "/trigger-services/<service_id>/triggers/<trigger_id>/details", methods=["GET"]
)
def get_trigger_details(service_id, trigger_id):
    """Get details for a specific trigger"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        details = owl_service.get_trigger_details(service_id, trigger_id)
        return jsonify([detail.to_dict() for detail in details])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/action-services", methods=["GET"])
def get_action_services():
    """Get all services that offer actions"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        services = owl_service.get_action_services()
        return jsonify([service.to_dict() for service in services])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/action-services/<service_id>/actions", methods=["GET"])
def get_actions(service_id):
    """Get actions for a specific service"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        actions = owl_service.get_actions(service_id)
        return jsonify([action.to_dict() for action in actions])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sifis_bp.route(
    "/action-services/<service_id>/actions/<action_id>/details", methods=["GET"]
)
def get_action_details(service_id, action_id):
    """Get details for a specific action"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        details = owl_service.get_action_details(service_id, action_id)
        return jsonify([detail.to_dict() for detail in details])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "owl_service": "available" if owl_service else "unavailable",
        }
    )


# ========== RULE ENDPOINTS ==========


@sifis_bp.route("/rule", methods=["GET"])
# @jwt_required() TODO: Uncomment when auth is ready
def get_rules():
    """Get all rules for the current user"""
    if not rule_service:
        return jsonify({"error": "Rule service not available"}), 500

    try:
        # username = get_jwt_identity()
        # user = user_repo.find_user_by_username(username)
        user = user_repo.get_user_by_uuid("03af6091-280d-457f-a131-689449a144d8")
        user.email = "ptp-demo"

        if not user:
            return jsonify({"error": "User not found"}), 404

        rules = rule_service.get_rules_by_type("sifis", user)

        # Convert Rule objects to dict for JSON serialization
        rules_data = []
        for rule in rules:
            rule_dict = {
                "dbId": rule.db_id,
                "type": rule.type,
                "effect": rule.effect,
                "subject": rule.subject,
                "timestamp": rule.timestamp,  # Already an integer (Unix timestamp in milliseconds)
                "trigger": rule.trigger.to_dict() if rule.trigger else None,
                "action": rule.action.to_dict() if rule.action else None,
            }
            rules_data.append(rule_dict)

        return jsonify(rules_data)
    except Exception as e:
        logging.error(f"Error getting rules: {e}")
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/rule", methods=["POST"])
# @jwt_required() TODO: Uncomment when auth is ready
def save_rule():
    """Save a new rule"""
    if not rule_service:
        return jsonify({"error": "Rule service not available"}), 500

    try:
        # username = get_jwt_identity()
        user = user_repo.get_user_by_uuid("03af6091-280d-457f-a131-689449a144d8")
        user.email = "ptp-demo"
        if not user:
            return jsonify({"error": "User not found"}), 404

        rule_data = request.get_json()

        if not rule_data:
            return jsonify({"error": "No data provided"}), 400

        # Validate request with schema (DTO pattern)
        schema = RuleRequestSchema()
        try:
            validated_data = schema.load(rule_data)
        except ValidationError as err:
            return jsonify({"error": "Validation failed", "details": err.messages}), 400

        rule_id = rule_service.save_rule(validated_data, "sifis", user)

        return jsonify({"id": rule_id}), 200
    except Exception as e:
        logging.error(f"Error saving rule: {e}")
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/rule/<int:rule_id>", methods=["DELETE"])
# @jwt_required() TODO: Uncomment when auth is ready
def delete_rule(rule_id):
    """Delete a rule by ID"""
    if not rule_service:
        return jsonify({"error": "Rule service not available"}), 500

    try:
        rule_service.delete_rule(rule_id)
        return jsonify({"id": rule_id}), 200
    except Exception as e:
        logging.error(f"Error deleting rule: {e}")
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/rule/trigger", methods=["GET"])
@jwt_required()
def get_defined_triggers():
    """Get all triggers defined in rules"""
    if not rule_service:
        return jsonify({"error": "Rule service not available"}), 500

    try:
        username = get_jwt_identity()
        user = user_repo.find_user_by_username(username)

        if not user:
            return jsonify({"error": "User not found"}), 404

        triggers = rule_service.get_defined_triggers_by_type("sifis", user)
        return jsonify([trigger.to_dict() for trigger in triggers])
    except Exception as e:
        logging.error(f"Error getting defined triggers: {e}")
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/translate", methods=["POST"])
# @jwt_required() TODO: Uncomment when auth is ready
def translate_rule():
    """Translate a rule into XACML policies and publish to DHT"""
    if not xacml_service or not dht_service:
        return jsonify({"error": "XACML or DHT service not available"}), 500

    try:
        # username = get_jwt_identity()
        user = user_repo.get_user_by_uuid("03af6091-280d-457f-a131-689449a144d8")
        user.email = "ptp-demo"

        if not user:
            return jsonify({"error": "User not found"}), 404

        rule_data = request.get_json()
        if not rule_data:
            return jsonify({"error": "No data provided"}), 400

        # Validate request with schema (DTO pattern)
        schema = RuleRequestSchema()
        try:
            validated_data = schema.load(rule_data)
        except ValidationError as err:
            return jsonify({"error": "Validation failed", "details": err.messages}), 400

        # Get policies directory from config
        policies_dir = Path(config["policies"]["directory"])
        policies_dir.mkdir(parents=True, exist_ok=True)

        # Clean directory
        for file in policies_dir.glob("*.xml"):
            file.unlink()

        # Translate rule to XACML policies
        policies_xml = xacml_service.translate(validated_data, user.email)

        # Save policies to files and publish to DHT
        for i, policy_xml in enumerate(policies_xml):
            # Extract policy ID from XML (simplified - just use timestamp-based)
            from datetime import datetime

            timestamp = int(datetime.now().timestamp() * 1000)
            policy_id = f"policy_{timestamp}_{i}"

            # Save to file
            policy_file = policies_dir / f"{policy_id}.xml"
            with open(policy_file, "w", encoding="utf-8") as f:
                f.write(policy_xml)

            # Publish to DHT
            dht_service.publish_policy(policy_xml, policy_id)

        return (
            jsonify({"message": "Policies translated and published successfully"}),
            200,
        )

    except Exception as e:
        logging.error(f"Error translating rule: {e}")
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/download", methods=["GET"])
# @jwt_required() TODO: Uncomment when auth is ready
def download_policies():
    """Download all policies as a ZIP file"""
    try:
        # Get policies directory
        policies_dir = Path(config["policies"]["directory"])

        if not policies_dir.exists() or not any(policies_dir.glob("*.xml")):
            return jsonify({"error": "No policies available for download"}), 404

        # Create ZIP file in memory
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for policy_file in policies_dir.glob("*.xml"):
                zf.write(policy_file, arcname=policy_file.name)

        memory_file.seek(0)

        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name="policies.zip",
        )

    except Exception as e:
        logging.error(f"Error downloading policies: {e}")
        return jsonify({"error": str(e)}), 500
