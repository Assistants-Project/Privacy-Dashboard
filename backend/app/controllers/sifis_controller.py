# app.py
from flask import jsonify, request
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity


from ..services import OWLService
from ..services.rule_service import RuleService
from ..repositories.user_repository import UserRepository

import logging

sifis_bp = Blueprint(
    "SIFIS API",
    "sifis_bp",
    url_prefix="/api/sifis",
    description="Endpoints for SIFIS",
)

# Initialize OWL Service
try:
    owl_service = OWLService()
    rule_service = RuleService(owl_service)
    user_repo = UserRepository()
    logging.info("OWL Service initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize OWL Service: {e}")
    owl_service = None
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

        # Convert to dict for JSON serialization
        rules_data = []
        for rule in rules:
            rule_dict = {
                "dbId": rule["db_id"],
                "type": rule["type"],
                "effect": rule["effect"],
                "subject": rule["subject"],
                "timestamp": rule[
                    "timestamp"
                ],  # Already an integer (Unix timestamp in milliseconds)
                "trigger": rule["trigger"].to_dict(),
                "action": rule["action"].to_dict(),
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

        rule_id = rule_service.save_rule(rule_data, "sifis", user)

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
