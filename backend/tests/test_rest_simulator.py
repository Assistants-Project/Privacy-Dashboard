"""Unit tests for RestSimulator"""
import pytest
from unittest.mock import Mock, MagicMock
from app.models.entities.petrinet.rest_simulator import RestSimulator
from app.models.entities.petrinet.petri_net import PetriNet
from app.models.entities.petrinet.transition import Transition, RuleTransition, CopyTransition
from app.models.entities.petrinet.place import Place
from app.models.entities.sifis.owl.rule import Rule


@pytest.fixture
def mock_petri_net():
    """Create a mock Petri Net"""
    net = Mock(spec=PetriNet)
    net.is_dead = Mock(return_value=False)
    return net


@pytest.fixture
def rest_simulator(mock_petri_net):
    """Create RestSimulator with mock net"""
    return RestSimulator(mock_petri_net)


class TestRestSimulator:
    """Test RestSimulator functionality"""
    
    def test_initialization(self, rest_simulator, mock_petri_net):
        """Test RestSimulator initialization"""
        assert rest_simulator.net == mock_petri_net
        assert rest_simulator.paused is False
        assert rest_simulator.stop is False
    
    def test_is_finished_when_dead(self, rest_simulator, mock_petri_net):
        """Test is_finished returns True when net is dead"""
        mock_petri_net.is_dead.return_value = True
        assert rest_simulator.is_finished() is True
    
    def test_is_finished_when_not_dead(self, rest_simulator, mock_petri_net):
        """Test is_finished returns False when net is not dead"""
        mock_petri_net.is_dead.return_value = False
        assert rest_simulator.is_finished() is False
    
    def test_step_returns_none_when_finished(self, rest_simulator, mock_petri_net):
        """Test step returns None when simulation is finished"""
        mock_petri_net.is_dead.return_value = True
        result = rest_simulator.step()
        assert result is None
    
    def test_enabled_transition_list(self, rest_simulator, mock_petri_net):
        """Test enabled_transition_list returns enabled transitions"""
        enabled_transition = Mock(spec=Transition)
        enabled_transition.enabled.return_value = True
        
        disabled_transition = Mock(spec=Transition)
        disabled_transition.enabled.return_value = False
        
        mock_petri_net.get_transitions.return_value = [
            enabled_transition,
            disabled_transition
        ]
        
        result = rest_simulator.enabled_transition_list()
        
        assert len(result) == 1
        assert result[0] == enabled_transition
    
    def test_fire_transition_with_rule_transition(self, rest_simulator, mock_petri_net):
        """Test fire_transition with a RuleTransition"""
        mock_rule = Mock(spec=Rule)
        rule_transition = Mock(spec=RuleTransition)
        rule_transition.enabled.return_value = True
        rule_transition.fire_and_get_rule.return_value = mock_rule
        
        mock_petri_net.get_transitions.return_value = [rule_transition]
        
        result = rest_simulator.fire_transition()
        
        assert result == mock_rule
        rule_transition.fire_and_get_rule.assert_called_once()
    
    
    def test_fire_transition_no_enabled_transitions(self, rest_simulator, mock_petri_net):
        """Test fire_transition returns None when no transitions enabled"""
        mock_petri_net.get_transitions.return_value = []
        
        result = rest_simulator.fire_transition()
        assert result is None
    
    def test_get_random_transition(self, rest_simulator, mock_petri_net):
        """Test get_random_transition returns a transition"""
        transitions = [Mock(spec=Transition) for _ in range(3)]
        for t in transitions:
            t.enabled.return_value = True
        
        mock_petri_net.get_transitions.return_value = transitions
        
        result = rest_simulator.get_random_transition()
        
        assert result in transitions
