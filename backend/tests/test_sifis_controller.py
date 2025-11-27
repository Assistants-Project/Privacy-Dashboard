"""Integration tests for SIFIS Controller endpoints"""
import pytest
import json


class TestOWLEndpoints:
    """Test OWL/Ontology query endpoints"""
    
    def test_get_trigger_services(self, client):
        """Test GET /api/sifis/trigger-services"""
        response = client.get("/api/sifis/trigger-services")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should return at least one trigger service"
        assert "id" in data[0], "Service should have an id"
        assert "name" in data[0], "Service should have a name"
    
    def test_get_triggers(self, client):
        """Test GET /api/sifis/trigger-services/{service}/triggers"""
        service = "sifis_time"
        response = client.get(f"/api/sifis/trigger-services/{service}/triggers")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0, f"Service {service} should have at least one trigger"
        assert "id" in data[0], "Trigger should have an id"
        assert "url" in data[0], "Trigger should have a url"
    
    def test_get_trigger_details(self, client):
        """Test GET /api/sifis/trigger-services/{service}/triggers/{trigger}/details"""
        service = "sifis_time"
        trigger = "sifis_every_afternoon_trigger"
        response = client.get(
            f"/api/sifis/trigger-services/{service}/triggers/{trigger}/details"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_get_action_services(self, client):
        """Test GET /api/sifis/action-services"""
        response = client.get("/api/sifis/action-services")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should return at least one action service"
        assert "id" in data[0], "Service should have an id"
    
    def test_get_actions(self, client):
        """Test GET /api/sifis/action-services/{service}/actions"""
        service = "sifis_video"
        response = client.get(f"/api/sifis/action-services/{service}/actions")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0, f"Service {service} should have at least one action"
        assert "id" in data[0], "Action should have an id"
        assert "url" in data[0], "Action should have a url"
    
    def test_get_action_details(self, client):
        """Test GET /api/sifis/action-services/{service}/actions/{action}/details"""
        service = "sifis_video"
        action = "sifis_record_video_action"
        response = client.get(
            f"/api/sifis/action-services/{service}/actions/{action}/details"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)



class TestRuleEndpoints:
    """Test rule management endpoints"""
    
    @pytest.fixture
    def sample_rule(self):
        """Sample rule payload"""
        return {
            "subject": "marketplace",
            "effect": "Deny",
            "timestamp": 1690467841444,
            "trigger": {
                "url": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_afternoon_trigger",
                "service": {"id": "sifis_time"},
                "details": [
                    {
                        "url": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_hour_from_detail",
                        "type": "value",
                        "value": "13"
                    },
                    {
                        "url": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_hour_to_detail",
                        "type": "value",
                        "value": "17"
                    }
                ]
            },
            "action": {
                "url": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_stop_record_video_action",
                "service": {"id": "sifis_video"},
                "details": [
                    {
                        "url": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_location_detail",
                        "type": "location",
                        "value": {
                            "name": "Living Room",
                            "url": "http://elite.polito.it/ontologies/sifis-home.owl/ptp-demo#location-livingroom"
                        }
                    }
                ]
            }
        }
    
    def test_get_rules(self, client):
        """Test GET /api/sifis/rule"""
        response = client.get("/api/sifis/rule")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_save_rule(self, client, sample_rule):
        """Test POST /api/sifis/rule"""
        response = client.post(
            "/api/sifis/rule",
            data=json.dumps(sample_rule),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "id" in data or "db_id" in data, "Response should contain rule ID"
        
        rule_id = data.get("id") or data.get("db_id")
        if rule_id:
            client.delete(f"/api/sifis/rule/{rule_id}")
    
    def test_delete_rule(self, client, sample_rule):
        """Test DELETE /api/sifis/rule/{id}"""
        response = client.post(
            "/api/sifis/rule",
            data=json.dumps(sample_rule),
            content_type="application/json"
        )
        data = response.get_json()
        rule_id = data.get("id") or data.get("db_id")
        
        response = client.delete(f"/api/sifis/rule/{rule_id}")
        assert response.status_code == 200
        delete_data = response.get_json()
        assert delete_data is not None, "Delete should return a response"
    
    def test_check_rule(self, client, sample_rule):
        """Test POST /api/sifis/check"""
        response = client.post(
            "/api/sifis/check",
            data=json.dumps(sample_rule),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict), "Should return a dictionary"
        assert "loops" in data or "inconsistencies" in data or "redundancies" in data, \
            "Should return RuleProblems structure with at least one problem type"



class TestPolicyEndpoints:
    """Test policy translation and download endpoints"""
    
    @pytest.fixture
    def sample_rule(self):
        """Sample rule for translation"""
        return {
            "subject": "marketplace",
            "effect": "Deny",
            "timestamp": 1690467841444,
            "trigger": {
                "url": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_afternoon_trigger",
                "service": {"id": "sifis_time"},
                "details": []
            },
            "action": {
                "url": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_stop_record_video_action",
                "service": {"id": "sifis_video"},
                "details": []
            }
        }
    
    def test_translate_rule(self, client, sample_rule):
        """Test POST /api/sifis/translate"""
        response = client.post(
            "/api/sifis/translate",
            data=json.dumps(sample_rule),
            content_type="application/json"
        )
        assert response.status_code == 200
    
    def test_download_policies(self, client):
        """Test GET /api/sifis/download"""
        response = client.get("/api/sifis/download")
        assert response.status_code in [200, 404]


class TestSimulationEndpoints:
    """Test new simulation endpoints (not in Java)"""
    
    @pytest.fixture
    def sample_trigger(self):
        """Sample trigger for simulation"""
        return {
            "trigger": {
                "url": "http://elite.polito.it/ontologies/sifis-home.owl#sifis_every_afternoon_trigger"
            }
        }
    
    def test_start_simulation(self, client, sample_trigger):
        """Test POST /api/sifis/simulation/start"""
        response = client.post(
            "/api/sifis/simulation/start",
            data=json.dumps(sample_trigger),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data or "db_id" in data
    
    def test_step_simulation(self, client):
        """Test POST /api/sifis/simulation/step"""
        response = client.post("/api/sifis/simulation/step")
        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data or "db_id" in data
    
    def test_stop_simulation(self, client):
        """Test POST /api/sifis/simulation/stop"""
        response = client.post("/api/sifis/simulation/stop")
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Simulation stopped"
    
    def test_simulation_flow(self, client, sample_trigger):
        """Test complete simulation flow: start -> step -> stop"""
        # Start
        response = client.post(
            "/api/sifis/simulation/start",
            data=json.dumps(sample_trigger),
            content_type="application/json"
        )
        assert response.status_code == 200
        
        # Step
        response = client.post("/api/sifis/simulation/step")
        assert response.status_code == 200
        
        # Stop
        response = client.post("/api/sifis/simulation/stop")
        assert response.status_code == 200
