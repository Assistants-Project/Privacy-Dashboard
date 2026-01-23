import React, { useState, useEffect } from "react";
import { Container, Row, Col, Form, Button, Tabs, Tab, Alert, Card, Navbar, Nav, Modal } from "react-bootstrap";

import { useNavigate } from "react-router-dom";
import { getHomes } from "../../API/homesAPI";
import { getRules, saveRule, deleteRule, translateRule, checkRule, downloadPolicies } from "../../API/sifisAPI";
import RuleList from "./RuleList";
import RuleEditor from "./RuleEditor";
import VerificationReport from "./VerificationReport";

function PolicyTranslation() {

  const navigate = useNavigate();
  
  const [homes, setHomes] = useState<any[]>([]);
  const [selectedHome, setSelectedHome] = useState<string>("");
  const [rules, setRules] = useState<any[]>([]);
  const [view, setView] = useState<"list" | "create">("list");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [verificationReport, setVerificationReport] = useState<any>(null);
  const [showReport, setShowReport] = useState(false);

  // Delete Modal State
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [ruleToDelete, setRuleToDelete] = useState<number | null>(null);

  // Load homes on mount
  useEffect(() => {
    getHomes()
      .then((data) => {
        setHomes(data);
        if (data.length > 0) setSelectedHome(data[0].uuid);
      })
      .catch((err) => setError("Failed to load homes: " + err.message));
  }, []);

  // Load rules when home changes
  useEffect(() => {
    if (selectedHome) loadRules();
  }, [selectedHome]);

  const loadRules = () => {
    getRules(selectedHome)
      .then(setRules)
      .catch((err) => console.error("Failed to load rules", err));
  };

  const handleCreateRule = async (rule: any) => {
    try {
      await saveRule(selectedHome, rule);
      setSuccess("Rule created successfully!");
      setView("list");
      loadRules();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message);
      setTimeout(() => setError(null), 5000);
    }
  };

  // Opens the modal
  const requestDeleteRule = (id: number) => {
    setRuleToDelete(id);
    setShowDeleteModal(true);
  };

  // Performs actual deletion
  const confirmDeleteRule = async () => {
    if (ruleToDelete === null) return;
    
    try {
      await deleteRule(selectedHome, ruleToDelete);
      setSuccess("Rule deleted.");
      loadRules();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
        setShowDeleteModal(false);
        setRuleToDelete(null);
        setShowReport(false); // Close report if open
    }
  };

  const cancelDelete = () => {
    setShowDeleteModal(false);
    setRuleToDelete(null);
  };

  const handleTranslateRule = async (id: number) => {
    try {
      await translateRule(selectedHome, id);
      setSuccess("Rule translated and published to DHT!");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError("Translation failed: " + err.message);
    }
  };
  
  const handleCheckRule = async (id: number) => {
      try {
          const res = await checkRule(selectedHome, id);
          setVerificationReport(res);
          setShowReport(true);
      } catch (err: any) {
          setError(err.message);
      }
  }

  const handleDownload = async () => {
      try {
          const blob = await downloadPolicies(selectedHome);
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "policies.zip";
          document.body.appendChild(a);
          a.click();
          a.remove();
      } catch (err: any) {
          setError("Download failed: " + err.message);
      }
  }

  return (
    <div className="d-flex flex-column" style={{ minHeight: "100vh" }}>
      <Navbar bg="dark" variant="dark" expand="lg" className="px-3">
        <Navbar.Brand href="#">SIFIS Policy Translation Point</Navbar.Brand>
        <Nav className="ms-auto">
             <Button variant="outline-light" size="sm" onClick={() => navigate("/")}>Back to Dashboard</Button>
        </Nav>
      </Navbar>

      <Container className="flex-grow-1 py-4">
        {error && <Alert variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}
        {success && <Alert variant="success" onClose={() => setSuccess(null)} dismissible>{success}</Alert>}

        <Card className="mb-4">
            <Card.Body className="d-flex align-items-center justify-content-between">
                <Form.Group as={Row} className="align-items-center m-0">
                    <Form.Label column sm="auto" className="fw-bold">Smart Home Context:</Form.Label>
                    <Col sm="auto">
                        <Form.Select 
                            value={selectedHome} 
                            onChange={(e) => setSelectedHome(e.target.value)}
                        >
                            {homes.map(h => <option key={h.uuid} value={h.uuid}>{h.name}</option>)}
                        </Form.Select>
                    </Col>
                </Form.Group>
                <div>
                     <Button variant="outline-dark" size="sm" onClick={handleDownload}>
                        Download All Policies (ZIP)
                     </Button>
                </div>
            </Card.Body>
        </Card>

        {selectedHome && (
            <>
            <Tabs defaultActiveKey="rules" id="ptp-tabs" className="mb-3">
                <Tab eventKey="rules" title="Policy Management">
                    {view === "list" ? (
                        <>
                            <div className="d-flex justify-content-between align-items-center mb-3">
                                <h3>Defined Policies</h3>
                                <Button variant="primary" onClick={() => setView("create")}>
                                    <i className="fa fa-plus me-2"></i>Create New Policy
                                </Button>
                            </div>
                            <RuleList 
                                rules={rules} 
                                onDelete={requestDeleteRule} 
                                onTranslate={handleTranslateRule}
                                onCheck={handleCheckRule}
                            />
                        </>
                    ) : (
                        <RuleEditor 
                            homeUuid={selectedHome} 
                            onSave={handleCreateRule} 
                            onCancel={() => setView("list")} 
                        />
                    )}
                </Tab>
            </Tabs>
            <VerificationReport 
                show={showReport} 
                onHide={() => setShowReport(false)} 
                report={verificationReport} 
                onDeleteRule={requestDeleteRule}
            />
            </>
        )}

        {/* Delete Confirmation Modal */}
        <Modal show={showDeleteModal} onHide={cancelDelete} centered>
            <Modal.Header closeButton>
                <Modal.Title>Confirm Deletion</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                Are you sure you want to delete this rule? This action cannot be undone.
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={cancelDelete}>
                    Cancel
                </Button>
                <Button variant="danger" onClick={confirmDeleteRule}>
                    Delete Rule
                </Button>
            </Modal.Footer>
        </Modal>

      </Container>
    </div>
  );
};

export default PolicyTranslation;
