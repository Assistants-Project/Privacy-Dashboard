"""
XACML Service for translating rules into XACML policies.

This service translates SIFIS-Home rules into XACML (eXtensible Access Control Markup Language)
policies that can be enforced by policy decision points.

This implementation produces XML output that closely matches the Java JAXB marshaller output,
including proper element ordering as per XACML 3.0 schema and condition elements.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from xml.etree.ElementTree import (
    Element,
    SubElement,
    tostring,
    QName,
    register_namespace,
)
from xml.dom import minidom

from ..models.entities.sifis.owl.action import Action
from ..models.entities.sifis.owl.command import Command
from ..models.entities.sifis.owl.trigger import Trigger
from ..models.entities.sifis.owl.detail import Detail

# Register XACML namespace
XACML_NS = "urn:oasis:names:tc:xacml:3.0:core:schema:wd-17"
register_namespace("", XACML_NS)


class XACMLService:
    """Service for translating rules into XACML policies."""

    def __init__(self, owl_service):
        """Initialize XACML service.

        Args:
            owl_service: OWL service instance for ontology queries
        """
        self.owl_service = owl_service
        self.logger = logging.getLogger(__name__)

    def translate(self, rule: Dict[str, Any], username: str) -> List[str]:
        """Translate a rule into XACML policy XML strings.

        Args:
            rule: Rule dictionary containing trigger, action, effect, and subject
            username: Username for context

        Returns:
            List of XACML policy XML strings
        """
        policies = []

        # Extract location from action details
        location = None
        action_data = rule.get("action", {})
        details = action_data.get("details", [])

        for detail in details:
            if detail.get("type") == "location":
                location = {
                    "name": detail.get("value", {}).get("name", "Unknown"),
                    "url": detail.get("value", {}).get("url", ""),
                }
                break

        if not location:
            location = {"name": "Unknown", "url": ""}

        # Get commands from OWL service
        try:
            action_obj = self._dict_to_action(action_data)
            commands = self.owl_service.get_commands(action_obj, location, username)
        except Exception as e:
            self.logger.error(f"Error getting commands: {e}", exc_info=True)
            commands = []

        effect = rule.get("effect", "Permit")
        subject = rule.get("subject", "user")
        trigger_data = rule.get("trigger")

        # Handle entire home vs specific location
        if location["name"] == "Entire Home" and commands:
            # Get device type from first command
            command = commands[0]
            device_type = command.entity.get("type") if command.entity else None

            # Check if action applies to all actions
            all_actions = action_data.get("id") == "Action"

            if subject == "marketplace":
                policy_xml = self._create_installation_policy(
                    effect, subject, trigger_data, command, device_type, all_actions
                )
            else:
                policy_xml = self._create_execution_policy(
                    effect, subject, trigger_data, command, device_type, all_actions
                )
            policies.append(policy_xml)
        else:
            # Create policy for each command
            all_actions = action_data.get("id") == "Action"

            for command in commands if commands else [None]:
                if subject == "marketplace":
                    policy_xml = self._create_installation_policy(
                        effect, subject, trigger_data, command, None, all_actions
                    )
                else:
                    policy_xml = self._create_execution_policy(
                        effect, subject, trigger_data, command, None, all_actions
                    )
                policies.append(policy_xml)

        return policies

    def _dict_to_action(self, action_data: Dict[str, Any]) -> Action:
        """Convert action dictionary to Action object."""
        from ..models.entities.sifis.owl.service import Service

        action = Action()
        action.url = action_data.get("url")
        action.id = action_data.get("id")
        action.name = action_data.get("name")
        action.description = action_data.get("description")

        service_data = action_data.get("service")
        if service_data:
            service = Service()
            service.id = service_data.get("id")
            service.name = service_data.get("name")
            action.service = service

        details = action_data.get("details", [])
        for detail_data in details:
            detail = Detail()
            detail.id = detail_data.get("id")
            detail.name = detail_data.get("name")
            detail.type = detail_data.get("type")
            detail.value = detail_data.get("value")
            action.details.append(detail)

        return action

    def _create_installation_policy(
        self,
        effect: str,
        subject: str,
        trigger: Optional[Dict],
        command: Optional["Command"],
        device_type: Optional[str],
        all_actions: bool,
    ) -> str:
        """Create installation policy XML."""
        timestamp = int(datetime.now().timestamp() * 1000)

        policy_name = "installation_"
        if all_actions:
            policy_name += "any_action"
        elif command and command.type:
            policy_name += command.type

        if device_type:
            policy_name += f"_{device_type}"
        elif command and command.entity and command.entity.get("id"):
            policy_name += f"_{command.entity.get('id')}"

        policy_id = f"{policy_name}_{timestamp}"

        # Select combining algorithm based on effect
        combining_alg = (
            "urn:oasis:names:tc:xacml:3.0:rule-combining-algorithm:permit-unless-deny"
            if effect == "Permit"
            else "urn:oasis:names:tc:xacml:3.0:rule-combining-algorithm:deny-unless-permit"
        )

        # Create Policy root element
        policy = Element(
            QName(XACML_NS, "Policy"),
            {
                "PolicyId": policy_id,
                "Version": "3.0",
                "RuleCombiningAlgId": combining_alg,
            },
        )

        # Description
        description = SubElement(policy, QName(XACML_NS, "Description"))
        description.text = f"XACML policy for SIFIS-Home - {timestamp}"

        # Target
        target = self._create_installation_target(subject)
        policy.append(target)

        # Rule
        rule_elem = self._create_installation_rule(
            effect, subject, trigger, command, device_type, all_actions
        )
        policy.append(rule_elem)

        # Default rule
        default_rule = self._create_default_permit_rule()
        policy.append(default_rule)

        return self._prettify_xml(policy)

    def _create_execution_policy(
        self,
        effect: str,
        subject: str,
        trigger: Optional[Dict],
        command: Optional["Command"],
        device_type: Optional[str],
        all_actions: bool,
    ) -> str:
        """Create execution policy XML matching Java JAXB output."""
        timestamp = int(datetime.now().timestamp() * 1000)

        policy_name = "execution_"
        if all_actions:
            policy_name += "any_action"
        elif command and command.type:
            policy_name += command.type

        if device_type:
            policy_name += f"_{device_type}"
        elif command and command.entity and command.entity.get("id"):
            policy_name += f"_{command.entity.get('id')}"

        policy_id = f"{policy_name}_{timestamp}"

        # Select combining algorithm based on effect
        combining_alg = (
            "urn:oasis:names:tc:xacml:3.0:rule-combining-algorithm:deny-unless-permit"
            if effect == "Permit"
            else "urn:oasis:names:tc:xacml:3.0:rule-combining-algorithm:permit-unless-deny"
        )

        # Create Policy root element
        policy = Element(
            QName(XACML_NS, "Policy"),
            {
                "PolicyId": policy_id,
                "Version": "3.0",
                "RuleCombiningAlgId": combining_alg,
            },
        )

        # Description
        description = SubElement(policy, QName(XACML_NS, "Description"))
        description.text = f"XACML policy for SIFIS-Home - {timestamp}"

        # Target
        target = self._create_execution_target(
            command.entity if command else None, subject, device_type
        )
        policy.append(target)

        # Rule
        rule_elem = self._create_execution_rule(
            effect, subject, trigger, command, all_actions
        )
        policy.append(rule_elem)

        # Default rule
        default_rule = self._create_default_deny_rule()
        policy.append(default_rule)

        return self._prettify_xml(policy)

    def _create_installation_target(self, subject: str) -> Element:
        """Create installation target element."""
        target = Element(QName(XACML_NS, "Target"))
        any_of = SubElement(target, QName(XACML_NS, "AnyOf"))
        all_of = SubElement(any_of, QName(XACML_NS, "AllOf"))

        # Subject match
        subject_match = self._create_match(
            "urn:oasis:names:tc:xacml:1.0:function:string-equal",
            subject,
            "http://www.w3.org/2001/XMLSchema#string",
            "urn:oasis:names:tc:xacml:1.0:subject:subject-id",
            "urn:oasis:names:tc:xacml:1.0:subject-category:access-subject",
        )
        all_of.append(subject_match)

        # Action match
        action_match = self._create_match(
            "urn:oasis:names:tc:xacml:1.0:function:string-equal",
            "install",
            "http://www.w3.org/2001/XMLSchema#string",
            "urn:oasis:names:tc:xacml:1.0:action:action-id",
            "urn:oasis:names:tc:xacml:3.0:attribute-category:action",
        )
        all_of.append(action_match)

        return target

    def _create_execution_target(
        self, entity: Optional[Dict], subject: str, device_type: Optional[str]
    ) -> Element:
        """Create execution target element."""
        target = Element(QName(XACML_NS, "Target"))
        any_of = SubElement(target, QName(XACML_NS, "AnyOf"))
        all_of = SubElement(any_of, QName(XACML_NS, "AllOf"))

        # Subject match
        subject_match = self._create_match(
            "urn:oasis:names:tc:xacml:1.0:function:string-equal",
            subject,
            "http://www.w3.org/2001/XMLSchema#string",
            "urn:oasis:names:tc:xacml:1.0:subject:subject-id",
            "urn:oasis:names:tc:xacml:1.0:subject-category:access-subject",
        )
        all_of.append(subject_match)

        # Resource match
        if entity:
            resource_match = self._create_match(
                "urn:oasis:names:tc:xacml:1.0:function:string-equal",
                entity.get("id", ""),
                "http://www.w3.org/2001/XMLSchema#string",
                "urn:oasis:names:tc:xacml:1.0:resource:resource-id",
                "urn:oasis:names:tc:xacml:3.0:attribute-category:resource",
            )
            all_of.append(resource_match)
        elif device_type:
            type_match = self._create_match(
                "urn:oasis:names:tc:xacml:1.0:function:string-equal",
                device_type,
                "http://www.w3.org/2001/XMLSchema#string",
                "eu.sifis-home:1.0:resource:device-type",
                "urn:oasis:names:tc:xacml:3.0:attribute-category:resource",
            )
            all_of.append(type_match)

        return target

    def _create_match(
        self, match_id: str, value: str, data_type: str, attr_id: str, category: str
    ) -> Element:
        """Create a match element."""
        match = Element(QName(XACML_NS, "Match"), {"MatchId": match_id})

        attr_value = SubElement(
            match, QName(XACML_NS, "AttributeValue"), {"DataType": data_type}
        )
        attr_value.text = value

        SubElement(
            match,
            QName(XACML_NS, "AttributeDesignator"),
            {
                "AttributeId": attr_id,
                "Category": category,
                "DataType": data_type,
                "MustBePresent": "true",
            },
        )

        return match

    def _create_installation_rule(
        self,
        effect: str,
        subject: str,
        trigger: Optional[Dict],
        command: Optional["Command"],
        device_type: Optional[str],
        all_actions: bool,
    ) -> Element:
        """Create installation rule element with conditions."""
        timestamp = int(datetime.now().timestamp() * 1000)

        rule = Element(
            QName(XACML_NS, "Rule"), {"RuleId": str(timestamp), "Effect": effect}
        )

        # Target (empty)
        SubElement(rule, QName(XACML_NS, "Target"))

        # PreCondition
        if device_type and all_actions:
            pre_cond = self._create_simple_condition(
                "pre",
                "device-type",
                device_type,
                "eu.sifis-home:1.0:resource:device:device-type",
                "urn:oasis:names:tc:xacml:3.0:attribute-category:resource",
            )
            rule.append(pre_cond)
        elif not all_actions and command:
            pre_cond = self._create_simple_condition(
                "pre",
                "action",
                command.type if command.type else "",
                "urn:oasis:names:tc:xacml:1.0:action:action-id",
                "urn:oasis:names:tc:xacml:3.0:attribute-category:action",
            )
            rule.append(pre_cond)

        # OngoingCondition
        if trigger and trigger.get("id") != "sifis_always_trigger":
            ongoing_cond = self._create_trigger_condition_element(trigger, "ongoing")
        else:
            ongoing_cond = self._create_simple_condition(
                "ongoing",
                "environment",
                "attribute-1-value",
                "urn:oasis:names:tc:xacml:3.0:environment:attribute-1",
                "urn:oasis:names:tc:xacml:3.0:attribute-category:environment",
            )
        rule.append(ongoing_cond)

        # PostCondition
        post_cond = self._create_simple_condition(
            "post",
            "subject",
            subject,
            "urn:oasis:names:tc:xacml:1.0:subject:subject-id",
            "urn:oasis:names:tc:xacml:1.0:subject-category:access-subject",
        )
        rule.append(post_cond)

        return rule

    def _create_execution_rule(
        self,
        effect: str,
        subject: str,
        trigger: Optional[Dict],
        command: Optional["Command"],
        all_actions: bool,
    ) -> Element:
        """Create execution rule element with conditions."""
        timestamp = int(datetime.now().timestamp() * 1000)

        rule = Element(
            QName(XACML_NS, "Rule"), {"RuleId": str(timestamp), "Effect": effect}
        )

        # Target (empty)
        SubElement(rule, QName(XACML_NS, "Target"))

        # PreCondition
        if not all_actions and command:
            pre_cond = self._create_simple_condition(
                "pre",
                "action",
                command.type if command.type else "",
                "urn:oasis:names:tc:xacml:1.0:action:action-id",
                "urn:oasis:names:tc:xacml:3.0:attribute-category:action",
            )
            rule.append(pre_cond)

        # OngoingCondition
        if trigger:
            ongoing_cond = self._create_trigger_condition_element(trigger, "ongoing")
        else:
            ongoing_cond = self._create_simple_condition(
                "ongoing",
                "environment",
                "attribute-1-value",
                "urn:oasis:names:tc:xacml:3.0:environment:attribute-1",
                "urn:oasis:names:tc:xacml:3.0:attribute-category:environment",
            )
        rule.append(ongoing_cond)

        # PostCondition
        post_cond = self._create_simple_condition(
            "post",
            "subject",
            subject,
            "urn:oasis:names:tc:xacml:1.0:subject:subject-id",
            "urn:oasis:names:tc:xacml:1.0:subject-category:access-subject",
        )
        rule.append(post_cond)

        return rule

    def _create_simple_condition(
        self,
        decision_time: str,
        cond_type: str,
        value: str,
        attr_id: str,
        category: str,
    ) -> Element:
        """Create a simple condition element matching Java JAXB structure exactly."""
        condition = Element(
            QName(XACML_NS, "Condition"), {"DecisionTime": decision_time}
        )

        # Root Apply (and) - contains one-and-only Apply and AttributeValue as siblings
        root_apply = SubElement(
            condition,
            QName(XACML_NS, "Apply"),
            {"FunctionId": "urn:oasis:names:tc:xacml:1.0:function:and"},
        )

        # One-and-only Apply (sibling to AttributeValue under 'and')
        one_only_apply = SubElement(
            root_apply,
            QName(XACML_NS, "Apply"),
            {"FunctionId": "urn:oasis:names:tc:xacml:1.0:function:string-one-and-only"},
        )

        # AttributeDesignator inside one-and-only
        SubElement(
            one_only_apply,
            QName(XACML_NS, "AttributeDesignator"),
            {
                "AttributeId": attr_id,
                "Category": category,
                "DataType": "http://www.w3.org/2001/XMLSchema#string",
                "MustBePresent": "true",
            },
        )

        # AttributeValue (sibling to one-and-only Apply under 'and')
        attr_value = SubElement(
            root_apply,
            QName(XACML_NS, "AttributeValue"),
            {"DataType": "http://www.w3.org/2001/XMLSchema#string"},
        )
        attr_value.text = value

        return condition

    def _create_trigger_condition_element(
        self, trigger: Dict, decision_time: str
    ) -> Element:
        """Create trigger-specific condition based on service type."""
        service_id = trigger.get("service", {}).get("id", "")

        if service_id == "sifis_time":
            return self._create_time_condition(trigger, decision_time)
        elif service_id == "sifis_windows":
            return self._create_windows_condition(trigger, decision_time)
        else:
            return self._create_simple_condition(
                decision_time,
                "environment",
                "attribute-1-value",
                "urn:oasis:names:tc:xacml:3.0:environment:attribute-1",
                "urn:oasis:names:tc:xacml:3.0:attribute-category:environment",
            )

    def _create_time_condition(self, trigger: Dict, decision_time: str) -> Element:
        """Create time-based condition."""
        condition = Element(
            QName(XACML_NS, "Condition"), {"DecisionTime": decision_time}
        )

        # Extract times
        from_time = "00:00:00+01:00"
        to_time = "23:59:59+01:00"
        details = trigger.get("details", [])
        for detail in details:
            name = detail.get("name", "").lower()
            value = detail.get("value")
            if value and "from" in name:
                from_time = f"{value}:00:00+01:00"
            elif value and "to" in name:
                to_time = f"{value}:00:00+01:00"

        # time-in-range Apply
        range_apply = SubElement(
            condition,
            QName(XACML_NS, "Apply"),
            {"FunctionId": "urn:oasis:names:tc:xacml:2.0:function:time-in-range"},
        )

        one_only = SubElement(
            range_apply,
            QName(XACML_NS, "Apply"),
            {"FunctionId": "urn:oasis:names:tc:xacml:1.0:function:time-one-and-only"},
        )

        SubElement(
            one_only,
            QName(XACML_NS, "AttributeDesignator"),
            {
                "AttributeId": "urn:oasis:names:tc:xacml:1.0:environment:current-time",
                "Category": "urn:oasis:names:tc:xacml:3.0:attribute-category:environment",
                "DataType": "http://www.w3.org/2001/XMLSchema#time",
                "MustBePresent": "true",
            },
        )

        from_val = SubElement(
            range_apply,
            QName(XACML_NS, "AttributeValue"),
            {"DataType": "http://www.w3.org/2001/XMLSchema#time"},
        )
        from_val.text = from_time

        to_val = SubElement(
            range_apply,
            QName(XACML_NS, "AttributeValue"),
            {"DataType": "http://www.w3.org/2001/XMLSchema#time"},
        )
        to_val.text = to_time

        return condition

    def _create_windows_condition(self, trigger: Dict, decision_time: str) -> Element:
        """Create windows trigger condition."""
        condition = Element(
            QName(XACML_NS, "Condition"), {"DecisionTime": decision_time}
        )

        trigger_id = trigger.get("id", "")
        bool_value = "true" if trigger_id == "sifis_windows_close_trigger" else "false"

        equal_apply = SubElement(
            condition,
            QName(XACML_NS, "Apply"),
            {"FunctionId": "urn:oasis:names:tc:xacml:1.0:function:boolean-equal"},
        )

        one_only = SubElement(
            equal_apply,
            QName(XACML_NS, "Apply"),
            {
                "FunctionId": "urn:oasis:names:tc:xacml:1.0:function:boolean-one-and-only"
            },
        )

        SubElement(
            one_only,
            QName(XACML_NS, "AttributeDesignator"),
            {
                "AttributeId": "eu:sifis-home:1.0:environment:all-windows-in-bedroom-closed",
                "Category": "urn:oasis:names:tc:xacml:3.0:attribute-category:environment",
                "DataType": "http://www.w3.org/2001/XMLSchema#boolean",
                "MustBePresent": "true",
            },
        )

        attr_val = SubElement(
            equal_apply,
            QName(XACML_NS, "AttributeValue"),
            {"DataType": "http://www.w3.org/2001/XMLSchema#boolean"},
        )
        attr_val.text = bool_value

        return condition

    def _create_default_deny_rule(self) -> Element:
        """Create default deny rule."""
        rule = Element(
            QName(XACML_NS, "Rule"),
            {"RuleId": "urn:oasis:names:tc:xacml:3.0:defdeny", "Effect": "Deny"},
        )

        description = SubElement(rule, QName(XACML_NS, "Description"))
        description.text = "Default Deny"

        SubElement(rule, QName(XACML_NS, "Target"))

        return rule

    def _create_default_permit_rule(self) -> Element:
        """Create default permit rule."""
        rule = Element(
            QName(XACML_NS, "Rule"), {"RuleId": "default-permit", "Effect": "Permit"}
        )

        description = SubElement(rule, QName(XACML_NS, "Description"))
        description.text = "Default Permit"

        SubElement(rule, QName(XACML_NS, "Target"))

        return rule

    def _prettify_xml(self, elem: Element) -> str:
        """Return a pretty-printed XML string."""
        rough_string = tostring(elem, encoding="utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
