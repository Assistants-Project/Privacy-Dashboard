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
from ..services.petrinet_service import PetriNetService
from ..repositories.user_repository import UserRepository
from ..schemas.request.rule_req_schema import RuleRequestSchema
from ..models.entities.sifis.owl.rule_problems import RuleProblems
from ..models.entities.petrinet import TriggerPlace, ActionPlace
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
    petrinet_service = PetriNetService(owl_service)
    user_repo = UserRepository()
    logging.info("Services initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize services: {e}")
    owl_service = None
    xacml_service = None
    dht_service = None
    rule_service = None
    petrinet_service = None


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
                "db_id": rule.db_id,
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


@sifis_bp.route("/check", methods=["POST"])
# @jwt_required() TODO: Uncomment when auth is ready
def check_rule():
    """Check a rule for loops, inconsistencies, and redundancies"""
    if not rule_service or not petrinet_service:
        return jsonify({"error": "Services not available"}), 500

    try:
        # Get user
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

        # Get Trigger and Action from OWL to ensure full details
        trigger = owl_service.get_trigger_by_url(
            validated_data["trigger"]["url"], user.email
        )
        action = owl_service.get_action_by_url(
            validated_data["action"]["url"], user.email
        )

        if not trigger or not action:
            return jsonify({"error": "Invalid trigger or action URL"}), 400

        # Populate details from validated data if present
        if "details" in validated_data.get("trigger", {}):
            for detail_data in validated_data["trigger"]["details"]:
                for detail in trigger.details:
                    if detail.url == detail_data.get("url"):
                        detail.value = detail_data.get("value")

        if "details" in validated_data.get("action", {}):
            for detail_data in validated_data["action"]["details"]:
                for detail in action.details:
                    if detail.url == detail_data.get("url"):
                        detail.value = detail_data.get("value")

        # Create Rule object
        from ..models.entities.sifis.owl.rule import Rule

        rule = Rule(
            db_id=validated_data.get("db_id"),
            effect=validated_data.get("effect"),
            subject=validated_data.get("subject"),
            timestamp=validated_data.get("timestamp"),
            trigger=trigger,
            action=action,
        )

        # Initialize RuleProblems
        rule_problems = RuleProblems()

        # Get all existing rules for Petri Net analysis
        rules_after = rule_service.get_rules_by_type("sifis", user)

        # If rule has db_id, find it in rules_after and use that version
        rule_problems.rule = rule  # Default to request rule
        if rule.db_id:
            for r in rules_after:
                if r.db_id == rule.db_id:
                    rule_problems.rule = r
                    break

        # Build Petri Net
        net = petrinet_service.get_net(user.email, rules_after, refresh=True)

        # Search for loops
        cycles = net.get_cycle(rule, rules_after)

        if cycles and len(cycles) > 0:
            # There are cycles!
            for cycle in cycles:
                loop = []
                cycle.reverse()

                i = 0
                while i < len(cycle):
                    if isinstance(cycle[i], TriggerPlace):
                        trigger_place = cycle[i]
                        if i + 1 < len(cycle) and isinstance(cycle[i + 1], ActionPlace):
                            action_place = cycle[i + 1]

                            # Create rule from trigger and action
                            r = Rule(
                                trigger=trigger_place.trigger,
                                action=action_place.action,
                            )

                            # Find matching rule in rules_after
                            for ra in rules_after:
                                if ra.trigger == r.trigger and ra.action == r.action:
                                    loop.append(ra)
                                    break
                        i += 2
                    else:
                        i += 1

                # Only add loop if the checked rule is involved
                if any(
                    r.trigger == rule.trigger and r.action == rule.action for r in loop
                ):
                    rule_problems.add_loop(loop)

        # If no loops, check for inconsistencies and redundancies
        if not rule_problems.loops:
            # Get root trigger
            start_trigger = net.get_root(rule)
            if not start_trigger:
                start_trigger = rule.trigger

            rule_problems.start_trigger = start_trigger

            # Simulate the Petri Net to get rules that would execute
            # Call the method on the net itself
            simulated_rules = net.get_simulated_rules(start_trigger)

            # Limit to 40 rules like Java
            if len(simulated_rules) > 40:
                simulated_rules = simulated_rules[:40]

            # Compare ALL rules against ALL rules
            for i in range(len(simulated_rules)):
                r1 = simulated_rules[i]
                a1 = r1.action
                redundant = [r1]
                inconsistent = [r1]

                for j in range(min(len(simulated_rules), 100)):  # j<100 check
                    if j != i:
                        r2 = simulated_rules[j]
                        a2 = r2.action

                        # Check if actions are equivalent
                        if owl_service.equals_ml(a1, a2):
                            redundant.append(r2)
                        else:
                            inconsistent.append(r2)

                # Only add if we found redundancies (more than just r1)
                if len(redundant) > 1 and not rule_problems.contains_redundancy(
                    redundant
                ):
                    # Check if the rule being validated is in this redundant group
                    rule_involved = any(
                        r.trigger.url == rule.trigger.url
                        and r.action.url == rule.action.url
                        for r in redundant
                    )
                    if rule_involved:
                        rule_problems.add_redundant_rules(redundant)

                # Only add if we found inconsistencies (more than just r1)
                if len(inconsistent) > 1 and not rule_problems.contains_inconsistency(
                    inconsistent
                ):
                    # Check if the rule being validated is in this inconsistent group
                    rule_involved = any(
                        r.trigger.url == rule.trigger.url
                        and r.action.url == rule.action.url
                        for r in inconsistent
                    )
                    if rule_involved:
                        rule_problems.add_inconsistent_rules(inconsistent)

            # Set parents for rules based on triggers
            last_trigger = simulated_rules[0].trigger if simulated_rules else None
            temp = []

            for simulated_rule in simulated_rules:
                if simulated_rule.trigger == last_trigger:
                    temp.append(simulated_rule)
                    continue

                simulated_rule.parents = petrinet_service.get_parents(
                    simulated_rule, temp
                )
                temp.append(simulated_rule)
                last_trigger = simulated_rule.trigger

            rule_problems.executed_rules = simulated_rules

        return jsonify(rule_problems.to_dict()), 200

    except Exception as e:
        logging.error(f"Error checking rule: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/simulation/start", methods=["POST"])
# @jwt_required() TODO: Uncomment when auth is ready
def start_simulation():
    """Start a step-by-step simulation"""
    if not petrinet_service or not rule_service:
        return jsonify({"error": "Services not available"}), 500

    try:
        # user = user_repo.find_user_by_username(get_jwt_identity())
        user = user_repo.get_user_by_uuid("03af6091-280d-457f-a131-689449a144d8")
        user.email = "ptp-demo"
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        if not data or "trigger" not in data:
            return jsonify({"error": "Trigger data required"}), 400

        # Get rules for user
        rules = rule_service.get_rules_by_type("sifis", user)

        # Parse trigger from request
        trigger_data = data["trigger"]
        # We need to reconstruct the Trigger object. 
        # Ideally we should use a schema, but for now we'll rely on OWL service to hydrate it
        # or construct it manually if it's a simple object.
        # Let's try to get it from OWL service if URL is present
        trigger = None
        if "url" in trigger_data:
            trigger = owl_service.get_trigger_by_url(trigger_data["url"], user.email)
        
        if not trigger:
             return jsonify({"error": "Invalid trigger"}), 400

        # Start simulation
        result_rule = petrinet_service.start_rest_simulation(trigger, rules, user.email)
        
        if result_rule:
            return jsonify(result_rule.to_dict()), 200
        else:
            return jsonify({"message": "Simulation started, no rule executed immediately"}), 200

    except Exception as e:
        logging.error(f"Error starting simulation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/simulation/step", methods=["POST"])
# @jwt_required() TODO: Uncomment when auth is ready
def step_simulation():
    """Execute next step in simulation"""
    if not petrinet_service:
        return jsonify({"error": "Services not available"}), 500

    try:
        # user = user_repo.find_user_by_username(get_jwt_identity())
        user = user_repo.get_user_by_uuid("03af6091-280d-457f-a131-689449a144d8")
        user.email = "ptp-demo"
        
        rule = petrinet_service.step_rest_simulation(user.email)
        
        if rule:
            return jsonify(rule.to_dict()), 200
        else:
            return jsonify({"message": "No rule executed in this step or simulation finished"}), 200

    except Exception as e:
        logging.error(f"Error stepping simulation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sifis_bp.route("/simulation/stop", methods=["POST"])
# @jwt_required() TODO: Uncomment when auth is ready
def stop_simulation():
    """Stop the simulation"""
    if not petrinet_service:
        return jsonify({"error": "Services not available"}), 500

    try:
        # user = user_repo.find_user_by_username(get_jwt_identity())
        user = user_repo.get_user_by_uuid("03af6091-280d-457f-a131-689449a144d8")
        user.email = "ptp-demo"
        
        petrinet_service.stop_rest_simulator(user.email)
        return jsonify({"message": "Simulation stopped"}), 200

    except Exception as e:
        logging.error(f"Error stopping simulation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
