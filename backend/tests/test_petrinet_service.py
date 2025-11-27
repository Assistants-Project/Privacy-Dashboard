"""Unit tests for PetriNetService"""
import pytest
from unittest.mock import Mock, MagicMock
from app.services.petrinet_service import PetriNetService
from app.services.owl_service import OWLService
from app.models.entities.sifis.owl.rule import Rule
from app.models.entities.sifis.owl.trigger import Trigger
from app.models.entities.sifis.owl.action import Action
from app.models.entities.sifis.owl.service import Service


@pytest.fixture
def mock_owl_service():
    """Mock OWL service"""
    service = Mock(spec=OWLService)
    service.triggers = Mock(return_value=False)
    return service


@pytest.fixture
def petrinet_service(mock_owl_service):
    """Create PetriNetService with mocked dependencies"""
    return PetriNetService(mock_owl_service)


@pytest.fixture
def sample_rules():
    """Create sample rules for testing"""
    service1 = Service(id="sifis_time", name="Time", url="http://example.com/time")
    service2 = Service(id="sifis_video", name="Video", url="http://example.com/video")
    
    trigger1 = Trigger(
        id="trigger1",
        name="Trigger 1",
        url="http://example.com/trigger1",
        service=service1,
        details=[]
    )
    
    action1 = Action(
        id="action1",
        name="Action 1",
        url="http://example.com/action1",
        service=service2,
        details=[]
    )
    
    rule1 = Rule(
        db_id=1,
        trigger=trigger1,
        action=action1,
        effect="Permit",
        subject="test"
    )
    
    return [rule1]


class TestPetriNetService:
    """Test PetriNetService functionality"""
    
    def test_get_net_creates_new_net(self, petrinet_service, sample_rules):
        """Test that get_net creates a new Petri Net"""
        username = "test_user"
        net = petrinet_service.get_net(username, sample_rules, refresh=False)
        
        assert net is not None
        assert net.label == username
        assert username in petrinet_service.nets
    
    def test_get_net_returns_cached_net(self, petrinet_service, sample_rules):
        """Test that get_net returns cached net when available"""
        username = "test_user"
        
        # First call creates net
        net1 = petrinet_service.get_net(username, sample_rules, refresh=False)
        
        # Second call should return same net
        net2 = petrinet_service.get_net(username, sample_rules, refresh=False)
        
        assert net1 is net2
    
    def test_get_net_refresh_creates_new_net(self, petrinet_service, sample_rules):
        """Test that refresh=True creates a new net"""
        username = "test_user"
        
        # First call
        net1 = petrinet_service.get_net(username, sample_rules, refresh=False)
        
        # Second call with refresh
        net2 = petrinet_service.get_net(username, sample_rules, refresh=True)
        
        assert net1 is not net2
    
    def test_start_rest_simulation(self, petrinet_service, sample_rules):
        """Test starting a REST simulation"""
        username = "test_user"
        trigger = sample_rules[0].trigger
        
        result = petrinet_service.start_rest_simulation(trigger, sample_rules, username)
        
        assert username in petrinet_service.simulators
    
    def test_step_rest_simulation_without_start(self, petrinet_service):
        """Test stepping simulation without starting returns None"""
        username = "test_user"
        result = petrinet_service.step_rest_simulation(username)
        assert result is None
    
    def test_stop_rest_simulator(self, petrinet_service, sample_rules):
        """Test stopping a simulation"""
        username = "test_user"
        trigger = sample_rules[0].trigger
        
        # Start simulation
        petrinet_service.start_rest_simulation(trigger, sample_rules, username)
        assert username in petrinet_service.simulators
        
        # Stop simulation
        petrinet_service.stop_rest_simulator(username)
        assert username not in petrinet_service.simulators
    
    def test_get_by_trigger(self, petrinet_service, sample_rules):
        """Test _get_by_trigger helper method"""
        trigger = sample_rules[0].trigger
        result = petrinet_service._get_by_trigger(sample_rules, trigger)
        
        assert len(result) == 1
        assert result[0] == sample_rules[0]
    
    def test_get_by_trigger_no_match(self, petrinet_service, sample_rules):
        """Test _get_by_trigger with no matching trigger"""
        different_trigger = Trigger(
            id="different",
            name="Different",
            url="http://example.com/different",
            service=Mock(),
            details=[]
        )
        
        result = petrinet_service._get_by_trigger(sample_rules, different_trigger)
        assert len(result) == 0
