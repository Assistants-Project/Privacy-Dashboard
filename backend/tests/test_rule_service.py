"""Unit tests for RuleService"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.services.rule_service import RuleService
from app.services.owl_service import OWLService
from app.models.entities.user import User, UserRole
from app.models.entities.sifis.db import DbRule
from app.models.entities.sifis.owl.trigger import Trigger
from app.models.entities.sifis.owl.action import Action
from app.models.entities.sifis.owl.service import Service


@pytest.fixture
def mock_owl_service():
    """Mock OWL service"""
    service = Mock(spec=OWLService)
    
    mock_trigger = Mock(spec=Trigger)
    mock_trigger.url = "http://example.com/trigger1"
    mock_trigger.details = []
    service.get_trigger_by_url.return_value = mock_trigger
    
    mock_action = Mock(spec=Action)
    mock_action.url = "http://example.com/action1"
    mock_action.details = []
    service.get_action_by_url.return_value = mock_action
    
    return service


@pytest.fixture
def rule_service(mock_owl_service):
    """Create RuleService with mocked dependencies"""
    return RuleService(mock_owl_service)


@pytest.fixture
def test_user():
    """Create a test user"""
    user = User(
        id=1,
        uuid="test-uuid",
        firstname="Test",
        lastname="User",
        email="test@example.com",
        role=UserRole.USER
    )
    return user


@pytest.fixture
def sample_rule_data():
    """Sample rule data for testing"""
    return {
        "effect": "Permit",
        "subject": "test",
        "timestamp": 1234567890000,
        "trigger": {
            "url": "http://example.com/trigger1",
            "service": {"id": "sifis_time"},
            "details": []
        },
        "action": {
            "url": "http://example.com/action1",
            "service": {"id": "sifis_video"},
            "details": []
        }
    }


class TestRuleService:
    """Test RuleService functionality"""
    
    @patch('app.services.rule_service.RuleRepository')
    def test_save_rule_creates_db_rule(self, mock_repo_class, rule_service, test_user, sample_rule_data):
        """Test that save_rule creates a DbRule"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        saved_rule = Mock(spec=DbRule)
        saved_rule.id = 123
        mock_repo.save_rule.return_value = saved_rule
        mock_repo.find_or_create_entity.return_value = None
        
        rule_service.rule_repo = mock_repo
        
        result = rule_service.save_rule(sample_rule_data, "sifis", test_user)
        
        assert result == 123
        mock_repo.save_rule.assert_called_once()
    
    @patch('app.services.rule_service.RuleRepository')
    def test_save_rule_with_timestamp(self, mock_repo_class, rule_service, test_user, sample_rule_data):
        """Test that save_rule uses provided timestamp"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        saved_rule = Mock(spec=DbRule)
        saved_rule.id = 123
        mock_repo.save_rule.return_value = saved_rule
        mock_repo.find_or_create_entity.return_value = None
        
        rule_service.rule_repo = mock_repo
        
        timestamp = sample_rule_data["timestamp"]
        rule_service.save_rule(sample_rule_data, "sifis", test_user)
        
        call_args = mock_repo.save_rule.call_args[0][0]
        assert call_args.timestamp == timestamp
    
    @patch('app.services.rule_service.RuleRepository')
    def test_get_rules_by_type(self, mock_repo_class, rule_service, test_user, mock_owl_service):
        """Test getting rules by type"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        mock_db_rule = Mock(spec=DbRule)
        mock_db_rule.id = 1
        mock_db_rule.type = "sifis"
        mock_db_rule.effect = "Permit"
        mock_db_rule.subject = "test"
        mock_db_rule.timestamp = 1234567890000
        mock_db_rule.triggers = [Mock()]
        mock_db_rule.actions = [Mock()]
        mock_db_rule.triggers[0].url = "http://example.com/trigger1"
        mock_db_rule.triggers[0].entity = None
        mock_db_rule.triggers[0].details = []
        mock_db_rule.actions[0].url = "http://example.com/action1"
        mock_db_rule.actions[0].entity = None
        mock_db_rule.actions[0].details = []
        
        mock_repo.get_rules_by_user_and_type.return_value = [mock_db_rule]
        
        rule_service.rule_repo = mock_repo
        
        result = rule_service.get_rules_by_type("sifis", test_user)
        
        assert len(result) == 1
        assert result[0].db_id == 1
        mock_repo.get_rules_by_user_and_type.assert_called_once_with(test_user, "sifis")
    
    @patch('app.services.rule_service.RuleRepository')
    def test_delete_rule_not_found(self, mock_repo_class, rule_service):
        """Test deleting a non-existent rule"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        mock_repo.get_rule_by_id.return_value = None
        
        rule_service.rule_repo = mock_repo
        
        rule_service.delete_rule(999)
        
        mock_repo.delete_rule.assert_not_called()
