
import pytest
from unittest.mock import MagicMock, patch
from app.services.petrinet_service import PetriNetService
from app.models.entities.sifis.owl.rule import Rule
from app.models.entities.sifis.owl.trigger import Trigger
from app.models.entities.sifis.owl.action import Action
from app.models.entities.petrinet import TriggerPlace, ActionPlace


import pytest
from unittest.mock import MagicMock, patch
from app.services.petrinet_service import PetriNetService
from app.models.entities.petrinet import TriggerPlace, ActionPlace

class TestPetriNetCycles:
    """Test suite for PetriNetService cycle detection logic"""

    def test_check_rule_extracts_rules_from_cycle(self):
        """Test that check_rule correctly converts Place cycles back to Rule objects"""
        # Service Setup
        mock_owl_service = MagicMock()
        petri_net_service = PetriNetService(mock_owl_service)

        # Rule 1 (Target): T1 -> A1
        target_rule = MagicMock()
        target_rule.trigger.url = "http://trigger1"
        target_rule.action.url = "http://action1"
        target_rule.db_id = 1
        # Configure to_dict to return a real dict
        target_rule.to_dict.return_value = {"id": 1, "desc": "Rule 1"}

        # Rule 2: T2 -> A2
        r2 = MagicMock()
        r2.trigger.url = "http://trigger2"
        r2.action.url = "http://action2"
        r2.db_id = 2
        r2.to_dict.return_value = {"id": 2, "desc": "Rule 2"}
        
        existing_rules = [r2]
        user_uuid = "test-user"

        # Mock the network and its cycle return
        mock_net = MagicMock()
        
        # Create a cycle: T1 -> A1
        p1 = MagicMock(spec=TriggerPlace)
        p1.get_trigger.return_value.url = "http://trigger1"
        
        p2 = MagicMock(spec=ActionPlace)
        p2.get_action.return_value.url = "http://action1"
        
        # Cycle: [p1, p2] matches target_rule (T1->A1)
        mock_net.get_cycle.return_value = [[p1, p2]]
        
        # Mock get_net to return our mock_net
        with patch.object(petri_net_service, 'get_net', return_value=mock_net):
            problems = petri_net_service.check_rule(target_rule, existing_rules, user_uuid)
            
            assert "loops" in problems
            loops = problems["loops"]
            assert loops is not None
            assert len(loops) == 1
            
            loop_rule_dicts = loops[0]
            
            # Should match the dict returned by target_rule.to_dict()
            assert len(loop_rule_dicts) == 1
            assert loop_rule_dicts[0] == {"id": 1, "desc": "Rule 1"}


