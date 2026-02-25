# app.py
from flask import jsonify, request, send_file
from flask_smorest import Blueprint
from ..utils import ds_required
from io import BytesIO
import zipfile
from pathlib import Path
import os

from ..services import OWLService, XACMLService
from ..services.rule_service import RuleService
from ..services.petrinet_service import PetriNetService
from ..repositories.user_repository import UserRepository
from ..services.home_service import SmartHomeService
from ..exceptions.entities.home_exception import SmartHomeNotFoundException, SmartHomeForbiddenException
from ..exceptions import (
    WrongUserCredentialsException,
    SmartotumServiceUnavailableException,
    SmartotumTimeoutException,
)
from ..schemas.request.rule_req_schema import RuleRequestSchema
from config import BaseConfig

import logging


sifis_bp = Blueprint(
    "SIFIS API",
    "sifis_bp",
    url_prefix="/api/sifis",
    description="Endpoints for SIFIS",
)

# Initialize Services
try:

    owl_config = {
        "ONTOLOGY_DIRECTORY": BaseConfig.ONTOLOGY_DIRECTORY,
        "ONTOLOGY_SIFIS_FILE": BaseConfig.ONTOLOGY_SIFIS_FILE,
        "LOGGING_LEVEL": BaseConfig.LOGGING_LEVEL
    }
    owl_service = OWLService(owl_config)
    xacml_service = XACMLService(owl_service)
    rule_service = RuleService(owl_service)
    petrinet_service = PetriNetService(owl_service)
    user_repo = UserRepository()
    logging.info("Services initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize services: {e}")
    owl_service = None
    xacml_service = None
    rule_service = None
    petrinet_service = None



@sifis_bp.route("/homes/<home_uuid>/trigger-services", methods=["GET"])
@ds_required()
def get_trigger_services(current_user, home_uuid):
    """Get all services that offer triggers"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        SmartHomeService.verify_home_access(home_uuid, current_user)
        
        services = owl_service.get_trigger_services(home_uuid)
        return jsonify([service.to_dict() for service in services])
    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logging.error(f"Error getting trigger services: {e}")
        return jsonify({"error": str(e)}), 500



@sifis_bp.route("/homes/<home_uuid>/trigger-services/<service_id>/triggers", methods=["GET"])
@ds_required()
def get_triggers(home_uuid, service_id, current_user):
    """Get triggers for a specific service"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        SmartHomeService.verify_home_access(home_uuid, current_user)
        triggers = owl_service.get_triggers(service_id, str(home_uuid))
        return jsonify([trigger.to_dict() for trigger in triggers])
    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sifis_bp.route(
    "/homes/<home_uuid>/trigger-services/<service_id>/triggers/<trigger_id>/details", methods=["GET"]
)
@ds_required()
def get_trigger_details(home_uuid, service_id, trigger_id, current_user):
    """Get details for a specific trigger"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        SmartHomeService.verify_home_access(home_uuid, current_user)
        details = owl_service.get_trigger_details(service_id, trigger_id, str(home_uuid))
        return jsonify([detail.to_dict() for detail in details])
    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/homes/<home_uuid>/action-services", methods=["GET"])
@ds_required()
def get_action_services(current_user, home_uuid):
    """Get all services that offer actions"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        SmartHomeService.verify_home_access(home_uuid, current_user)
        services = owl_service.get_action_services(home_uuid)
        return jsonify([service.to_dict() for service in services])
    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/homes/<home_uuid>/action-services/<service_id>/actions", methods=["GET"])
@ds_required()
def get_actions(home_uuid, service_id, current_user):
    """Get actions for a specific service"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        SmartHomeService.verify_home_access(home_uuid, current_user)
        actions = owl_service.get_actions(service_id, str(home_uuid))
        return jsonify([action.to_dict() for action in actions])
    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sifis_bp.route(
    "/homes/<home_uuid>/action-services/<service_id>/actions/<action_id>/details", methods=["GET"]
)
@ds_required()
def get_action_details(home_uuid, service_id, action_id, current_user):
    """Get details for a specific action"""
    if not owl_service:
        return jsonify({"error": "OWL Service not available"}), 500

    try:
        SmartHomeService.verify_home_access(home_uuid, current_user)
        details = owl_service.get_action_details(service_id, action_id, str(home_uuid))
        return jsonify([detail.to_dict() for detail in details])
    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "owl_service": "available" if owl_service else "unavailable",
            "flask_env": os.getenv("FLASK_ENV"),
            "smartotum_mock": os.getenv("FLASK_ENV") == "testing",
        }
    )


# ========== RULE ENDPOINTS ==========


@sifis_bp.route("/homes/<home_uuid>/rules", methods=["GET"])
@ds_required()
def get_rules(current_user, home_uuid):
    """Get all rules for the current user in a specific home"""
    if not rule_service:
        return jsonify({"error": "Rule service not available"}), 500

    try:
        user = current_user
        if not user:
            return jsonify({"error": "User not found"}), 404

        home = SmartHomeService.verify_home_access(home_uuid, user)
        rules = rule_service.get_rules_by_type("sifis", home)

        # Convert Rule objects to dict for JSON serialization
        rules_data = []
        for rule in rules:
            rule_dict = {
                "db_id": rule.db_id,
                "type": rule.type,
                "effect": rule.effect,
                "subject": rule.subject,
                "timestamp": rule.timestamp,
                "expirationDate": rule.expiration_date,
                "trigger": rule.trigger.to_dict() if rule.trigger else None,
                "action": rule.action.to_dict() if rule.action else None,
            }
            rules_data.append(rule_dict)

        return jsonify(rules_data)
    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logging.error(f"Error getting rules: {e}")
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/homes/<home_uuid>/rules", methods=["POST"])
@sifis_bp.arguments(RuleRequestSchema, as_kwargs=True)
@ds_required()
def save_rule(current_user, home_uuid, **rule_data):
    """Save a new rule"""
    if not rule_service:
        return jsonify({"error": "Rule service not available"}), 500

    try:
        user = current_user
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        home = SmartHomeService.verify_home_access(home_uuid, user)
        rule_id = rule_service.save_rule(rule_data, "sifis", home)

        return jsonify({"id": rule_id}), 200
    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except WrongUserCredentialsException as e:
        return jsonify({"error": str(e)}), e.code
    except (SmartotumServiceUnavailableException, SmartotumTimeoutException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logging.error(f"Error saving rule: {e}")
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/homes/<home_uuid>/rules/<int:rule_id>", methods=["DELETE"])
@ds_required()
def delete_rule(home_uuid, rule_id, current_user):
    """Delete a rule by ID"""
    if not rule_service:
        return jsonify({"error": "Rule service not available"}), 500

    try:
        # Get authenticated user
        user = current_user
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        home = SmartHomeService.verify_home_access(home_uuid, user)
        
        # Delete rule through service layer (proper architecture)
        deleted = rule_service.delete_rule_by_home(rule_id, home)
        
        if not deleted:
            return jsonify({"error": "Rule not found or access denied"}), 404
        
        return jsonify({"id": rule_id}), 200
    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logging.error(f"Error deleting rule: {e}")
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/homes/<home_uuid>/rules/triggers", methods=["GET"])
@ds_required()
def get_defined_triggers(current_user, home_uuid):
    """Get all triggers defined in rules"""
    if not rule_service:
        return jsonify({"error": "Rule service not available"}), 500

    try:
        user = current_user

        if not user:
            return jsonify({"error": "User not found"}), 404

        home = SmartHomeService.verify_home_access(home_uuid, user)
        triggers = rule_service.get_defined_triggers_by_type("sifis", home)
        return jsonify([trigger.to_dict() for trigger in triggers])
    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logging.error(f"Error getting defined triggers: {e}")
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/homes/<home_uuid>/rules/<int:rule_id>/download", methods=["POST"])
@ds_required()
def download_rule(home_uuid, rule_id, current_user):
    """Translate a rule into XACML policies and download"""
    if not rule_service or not xacml_service:
        return jsonify({"error": "Services not available"}), 500

    try:
        user = current_user
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Verify rule ownership
        home = SmartHomeService.verify_home_access(home_uuid, user)
        if not rule_service.verify_rule_ownership(rule_id, home):
             return jsonify({"error": "Rule not found or access denied"}), 404

        # Use new service method
        xacml_policies = rule_service.translate_rule(
            rule_id, home, xacml_service
        )
        
        if not xacml_policies:
             return jsonify({"error": "Failed to translate rule"}), 500

        # If single policy, return as XML file
        if len(xacml_policies) == 1:
            mem = BytesIO()
            mem.write(xacml_policies[0].encode("utf-8"))
            mem.seek(0)
            return send_file(
                mem,
                as_attachment=True,
                download_name=f"rule_{rule_id}.xml",
                mimetype="application/xml"
            )
        
        # If multiple policies, return as ZIP
        mem = BytesIO()
        with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, policy in enumerate(xacml_policies):
                zf.writestr(f"rule_{rule_id}_{i}.xml", policy)
        mem.seek(0)
        
        return send_file(
            mem,
            as_attachment=True,
            download_name=f"rule_{rule_id}.zip",
            mimetype="application/zip"
        )

    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logging.error(f"Error translating rule: {e}")
        return jsonify({"error": str(e)}), 500





@sifis_bp.route("/homes/<home_uuid>/rules/<int:rule_id>/check", methods=["GET"])
@ds_required()
def check_rule(home_uuid, rule_id, current_user):
    """Check a rule for loops, inconsistencies, and redundancies"""
    if not rule_service or not petrinet_service:
        return jsonify({"error": "Services not available"}), 500

    try:
        # Get user
        user = current_user
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Verify rule ownership and get rehydrated rule
        home = SmartHomeService.verify_home_access(home_uuid, user)
        rule = rule_service.get_rule_by_id(rule_id, home)
        if not rule:
             return jsonify({"error": "Rule not found or access denied"}), 404

        # Get all existing rules
        rules = rule_service.get_rules_by_type("sifis", home)

        # Check rule using PetriNet service logic
        result = petrinet_service.check_rule(rule, rules, str(home.uuid))

        return jsonify(result), 200

    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logging.error(f"Error checking rule: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/homes/<home_uuid>/simulation/start", methods=["POST"])
@ds_required()
def start_simulation(current_user, home_uuid):
    """Start a step-by-step simulation"""
    if not petrinet_service or not rule_service:
        return jsonify({"error": "Services not available"}), 500

    try:
        user = current_user
        if not user:
            return jsonify({"error": "User not found"}), 404

        home = SmartHomeService.verify_home_access(home_uuid, user)
        data = request.get_json()
        if not data or "trigger" not in data:
            return jsonify({"error": "Trigger data required"}), 400

        # Get rules for user
        rules = rule_service.get_rules_by_type("sifis", home)

        # Parse trigger from request
        trigger_data = data["trigger"]
  
        trigger = None
        if "url" in trigger_data:
            trigger = owl_service.get_trigger_by_url(trigger_data["url"], str(home.uuid))
        
        if not trigger:
             return jsonify({"error": "Invalid trigger"}), 400

        # Start simulation
        result_rule = petrinet_service.start_rest_simulation(trigger, rules, str(home.uuid))
        
        if result_rule:
             return jsonify(result_rule.to_dict()), 200
        else:
             return jsonify({"message": "Simulation started, no rule executed immediately"}), 200

    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logging.error(f"Error starting simulation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/homes/<home_uuid>/simulation/step", methods=["POST"])
@ds_required()
def step_simulation(current_user, home_uuid):
    """Execute next step in simulation"""
    if not petrinet_service:
        return jsonify({"error": "Services not available"}), 500

    try:
        user = current_user
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        home = SmartHomeService.verify_home_access(home_uuid, user)
        rule = petrinet_service.step_rest_simulation(str(home.uuid))
        
        if rule:
             return jsonify(rule.to_dict()), 200
        else:
             return jsonify({"message": "No rule executed in this step or simulation finished"}), 200

    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logging.error(f"Error stepping simulation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/homes/<home_uuid>/simulation/stop", methods=["POST"])
@ds_required()
def stop_simulation(current_user, home_uuid):
    """Stop the simulation"""
    if not petrinet_service:
        return jsonify({"error": "Services not available"}), 500

    try:
        user = current_user
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        home = SmartHomeService.verify_home_access(home_uuid, user)
        petrinet_service.stop_rest_simulator(str(home.uuid))
        return jsonify({"message": "Simulation stopped"}), 200

    except (SmartHomeNotFoundException, SmartHomeForbiddenException) as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logging.error(f"Error stopping simulation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
