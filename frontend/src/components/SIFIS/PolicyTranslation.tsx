import React, { useState, useEffect } from "react";
import {
  Container,
  Row,
  Col,
  Button,
  Tabs,
  Tab,
  Alert,
  Card,
  Navbar,
  Nav,
  Modal,
} from "react-bootstrap";

import { useNavigate } from "react-router-dom";
import { useHome } from "../HomeContext";
import {
  getRules,
  saveRule,
  deleteRule,
  translateRule,
  checkRule,
  downloadPolicies,
} from "../../API/SIFIS/sifisAPI";
import RuleList from "./RuleList";
import RuleEditor from "./RuleEditor";
import VerificationReport from "./VerificationReport";

function PolicyTranslation() {
  const navigate = useNavigate();
  const { current_home_uuid } = useHome(); // Consume Global Context

  const [rules, setRules] = useState<any[]>([]);
  const [view, setView] = useState<"list" | "create">("list");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [verificationReport, setVerificationReport] = useState<any>(null);
  const [showReport, setShowReport] = useState(false);

  // Delete Modal State
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [ruleToDelete, setRuleToDelete] = useState<number | null>(null);

  // Load rules when global current_home_uuid changes
  useEffect(() => {
    if (current_home_uuid) {
      loadRules();
    } else {
      setRules([]);
    }
  }, [current_home_uuid]);

  const loadRules = () => {
    if (!current_home_uuid) return;
    getRules(current_home_uuid)
      .then(setRules)
      .catch((err) => console.error("Failed to load rules", err));
  };

  const handleCreateRule = async (rule: any) => {
    if (!current_home_uuid) return;
    try {
      await saveRule(current_home_uuid, rule);
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
    if (ruleToDelete === null || !current_home_uuid) return;

    try {
      await deleteRule(current_home_uuid, ruleToDelete);
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
    if (!current_home_uuid) return;
    try {
      await translateRule(current_home_uuid, id);
      setSuccess("Rule translated and published to DHT!");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError("Translation failed: " + err.message);
    }
  };

  const handleCheckRule = async (id: number) => {
    if (!current_home_uuid) return;
    try {
      const res = await checkRule(current_home_uuid, id);
      setVerificationReport(res);
      setShowReport(true);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDownload = async () => {
    if (!current_home_uuid) return;
    try {
      const blob = await downloadPolicies(current_home_uuid);
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
  };

  return (
    <div className="d-flex flex-column" style={{ minHeight: "100vh" }}>
      <Navbar bg="dark" variant="dark" expand="lg" className="px-3">
        <Navbar.Brand href="#">SIFIS Policy Translation Point</Navbar.Brand>
        <Nav className="ms-auto">
          <Button
            variant="outline-light"
            size="sm"
            onClick={() => navigate("/")}
          >
            Back to Dashboard
          </Button>
        </Nav>
      </Navbar>

      <Container className="flex-grow-1 py-4">
        {error && (
          <Alert variant="danger" onClose={() => setError(null)} dismissible>
            {error}
          </Alert>
        )}
        {success && (
          <Alert variant="success" onClose={() => setSuccess(null)} dismissible>
            {success}
          </Alert>
        )}

        <Card className="mb-4">
          <Card.Body className="d-flex align-items-center justify-content-between">
            <div className="fw-bold">Policy Management</div>
            <div>
              <Button
                variant="outline-dark"
                size="sm"
                onClick={handleDownload}
                disabled={!current_home_uuid}
              >
                Download All Policies (ZIP)
              </Button>
            </div>
          </Card.Body>
        </Card>

        {current_home_uuid ? (
          <>
            <Tabs defaultActiveKey="rules" id="ptp-tabs" className="mb-3">
              <Tab eventKey="rules" title="Policy Management">
                {view === "list" ? (
                  <>
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <h3>Defined Policies</h3>
                      <Button
                        variant="primary"
                        onClick={() => setView("create")}
                      >
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
                    homeUuid={current_home_uuid}
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
        ) : (
          <Alert variant="info">
            Please select a Smart Home from the Dashboard Home Page to manage
            policies.
          </Alert>
        )}

        {/* Delete Confirmation Modal */}
        <Modal show={showDeleteModal} onHide={cancelDelete} centered>
          <Modal.Header closeButton>
            <Modal.Title>Confirm Deletion</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            Are you sure you want to delete this rule? This action cannot be
            undone.
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
}

export default PolicyTranslation;
