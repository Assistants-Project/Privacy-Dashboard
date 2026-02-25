import React, { useState, useEffect } from "react";
import {
  Container,
  Button,
  Tabs,
  Tab,
  Alert,
  Card,
  Modal,
  Col,
  Row,
  Spinner,
} from "react-bootstrap";

import { useHome } from "../../contexts/HomeContext";
import {
  getRules,
  saveRule,
  deleteRule,
  downloadRule,
  checkRule,
} from "../../API/SIFIS/sifisAPI";
import RuleList from "../../components/PolicyTranslation/RuleList";
import RuleEditor from "../../components/PolicyTranslation/RuleEditor";
import VerificationReport from "../../components/PolicyTranslation/VerificationReport";

function PolicyTranslation() {
  const { current_home_uuid } = useHome();

  const [rules, setRules] = useState<any[]>([]);
  const [rulesLoading, setRulesLoading] = useState(false);
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
      setRulesLoading(false);
    }
  }, [current_home_uuid]);

  const loadRules = () => {
    if (!current_home_uuid) return;
    setRulesLoading(true);
    getRules(current_home_uuid)
      .then(setRules)
      .catch((err) => console.error("Failed to load rules", err))
      .finally(() => setRulesLoading(false));
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

  const handleDownloadRule = async (id: number) => {
    if (!current_home_uuid) return;
    try {
      await downloadRule(current_home_uuid, id);
      setSuccess("Rule downloaded successfully!");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError("Download failed: " + err.message);
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

  return (
    <div className="d-flex flex-column h-100" style={{ overflow: "hidden" }}>
      <Container
        className="d-flex flex-column flex-grow-1 py-4"
        style={{ overflow: "hidden", minHeight: 0 }}
      >
        <div className="flex-shrink-0">
          {error && (
            <Alert variant="danger" onClose={() => setError(null)} dismissible>
              {error}
            </Alert>
          )}
          {success && (
            <Alert
              variant="success"
              onClose={() => setSuccess(null)}
              dismissible
            >
              {success}
            </Alert>
          )}
        </div>

        <div className="flex-grow-1" style={{ minHeight: 0, overflow: "hidden" }}>
          {current_home_uuid ? (
            <>
              {view === "list" ? (
                <>
                  <Card className="h-100 p-0">
                    <Card.Header className="bg-white d-flex align-items-center">
                      <div className="fw-semibold">Policy Translation</div>
                      <div className="ms-auto">
                      <Button
                        className="circular-button me-0"
                        style={{ color: "#181d1f" }}
                        onClick={() => setView("create")}
                        aria-label="Create policy"
                        title="Create policy"
                      >
                        <i className="fa-solid fa-plus"></i>
                      </Button>
                      </div>
                    </Card.Header>
                    <Card.Body style={{ minHeight: 0, overflow: "auto" }}>
                      {rulesLoading ? (
                        <div className="text-center text-muted mt-5">
                          <Spinner
                            animation="border"
                            size="sm"
                            className="me-2"
                          />
                          Loading rules...
                        </div>
                      ) : (
                        <RuleList
                          rules={rules}
                          onDelete={requestDeleteRule}
                          onDownload={handleDownloadRule}
                          onCheck={handleCheckRule}
                        />
                      )}
                    </Card.Body>
                  </Card>
                </>
              ) : (
                <RuleEditor
                  homeUuid={current_home_uuid}
                  onSave={handleCreateRule}
                  onCancel={() => setView("list")}
                />
              )}

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
        </div>

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
