import React from "react";
import { Button, Badge, Row, Col, Card } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { useApp } from "../../contexts/AppsContext";

interface Detail {
  name: string;
  value: any;
  type: string;
  url: string;
}

interface Service {
  name: string;
  description?: string;
}

interface TriggerAction {
  name?: string;
  description: string;
  url: string;
  service?: Service;
  details: Detail[];
}

interface Rule {
  db_id: number;
  consent_uuid?: string | null;
  consent_application_uuid?: string | null;
  type: string;
  effect: string; // "permit" or "deny"
  subject: string;
  timestamp: number;
  expirationDate?: string;
  trigger: TriggerAction;
  action: TriggerAction;
}

interface RuleListProps {
  rules: Rule[];
  onDelete: (id: number) => void;
  onDownload: (id: number) => void;
  onCheck: (id: number) => void;
}

const RuleList: React.FC<RuleListProps> = ({
  rules,
  onDelete,
  onDownload,
  onCheck,
}) => {
  const navigate = useNavigate();
  const { setSelectedAppUUID } = useApp();

  const openConsentApp = (applicationUuid: string | null | undefined) => {
    if (!applicationUuid) return;
    setSelectedAppUUID(applicationUuid);
    navigate("/installed-apps");
  };

  const renderDetails = (details: Detail[]) => {
    if (!details || details.length === 0) return null;
    return (
      <div className="mt-2 ps-3 border-start">
        {details.map((d, idx) => {
          let displayValue = d.value;

          if (Array.isArray(d.value)) {
            displayValue = d.value
              .map((v: any) => String(v).replace(/['"]/g, ""))
              .join(", ");
          } else if (typeof d.value === "string" && d.value.startsWith("[")) {
            displayValue = d.value.replace(/[\[\]'"]/g, "");
          } else if (typeof d.value === "object" && d.value) {
            displayValue = d.value.name || JSON.stringify(d.value);
          }

          const isDeviceDetail =
            (typeof d.type === "string" &&
              (d.type.toLowerCase() === "device" ||
                d.type.toLowerCase() === "entity")) ||
            (typeof d.name === "string" && d.name.toLowerCase().includes("device"));
          if (isDeviceDetail) {
            const trimmed =
              typeof displayValue === "string" ? displayValue.trim() : displayValue;
            if (
              displayValue === null ||
              displayValue === undefined ||
              (typeof displayValue === "string" && trimmed === "")
            ) {
              displayValue = "Any";
            }
          }

          return (
            <div key={idx} className="text-muted small">
              <strong>{d.name || "Parameter"}:</strong> {displayValue}
            </div>
          );
        })}
      </div>
    );
  };

  if (!rules || rules.length === 0) {
    return (
      <p className="text-muted text-center mt-5">
        No rules defined for this home.
      </p>
    );
  }

  return (
    <>
      <div className="d-flex flex-column gap-3">
        {rules.map((rule, idx) => (
          <Card key={rule.db_id} className="shadow-sm">
            <Card.Header className="bg-white py-2">
              <div className="d-flex align-items-center w-100 gap-3">
                <span className="text-muted small fw-bold">#{idx + 1}</span>
                <span className="text-muted small">ID {rule.db_id}</span>
                <Badge
                  bg={rule.effect === "permit" ? "success" : "danger"}
                  className="me-2"
                >
                  {rule.effect.toUpperCase()}
                </Badge>
                {!!rule.consent_uuid && (
                  <Badge
                    bg="secondary"
                    className="me-2"
                    role={rule.consent_application_uuid ? "button" : undefined}
                    tabIndex={rule.consent_application_uuid ? 0 : undefined}
                    style={
                      rule.consent_application_uuid
                        ? { cursor: "pointer", textUnderlineOffset: "2px" }
                        : undefined
                    }
                    title={
                      rule.consent_application_uuid
                        ? `Consent rule (managed automatically)\nClick to open the related app\nConsent UUID: ${rule.consent_uuid}`
                        : `Consent rule (managed automatically)\nConsent UUID: ${rule.consent_uuid}`
                    }
                    onClick={() => openConsentApp(rule.consent_application_uuid)}
                    onKeyDown={(e) => {
                      if (!rule.consent_application_uuid) return;
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        openConsentApp(rule.consent_application_uuid);
                      }
                    }}
                  >
                    CONSENT RULE
                    {rule.consent_application_uuid ? (
                      <i
                        className="fa-solid fa-arrow-up-right-from-square ms-1"
                        aria-hidden="true"
                      ></i>
                    ) : null}
                  </Badge>
                )}
                <span className="fw-bold text-dark">
                  {rule.trigger?.service?.name || "Trigger"}
                </span>
                <small className="text-muted">➜</small>
                <span className="fw-bold text-dark">
                  {rule.action?.service?.name || "Action"}
                </span>
                {!!rule.consent_uuid && (
                  <small className="text-muted ms-2" title="This rule is created/removed automatically when a consent is withdrawn/accepted">
                    Managed automatically
                  </small>
                )}

                {rule.expirationDate && (
                  <span className="text-muted small ms-2">
                    (Expires:{" "}
                    {rule.expirationDate.split(/[-/]/).reverse().join("/")})
                  </span>
                )}

                <div className="ms-auto d-flex align-items-center gap-3">
                  <small className="text-muted border-end pe-3 me-1">
                    Subject: {rule.subject.split("@")[0]}
                  </small>
                  <div className="d-flex gap-2">
                    <Button
                      variant="outline-success"
                      size="sm"
                      onClick={() => onDownload(rule.db_id)}
                    >
                      Download
                    </Button>
                    <Button
                      variant="outline-primary"
                      size="sm"
                      onClick={() => onCheck(rule.db_id)}
                    >
                      Check
                    </Button>
                    <Button
                      variant="outline-danger"
                      size="sm"
                      disabled={!!rule.consent_uuid}
                      title={
                        rule.consent_uuid
                          ? "Cannot delete consent related rule"
                          : "Delete"
                      }
                      onClick={() => {
                        if (rule.consent_uuid) return;
                        onDelete(rule.db_id);
                      }}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            </Card.Header>
            <Card.Body className="py-2">
              <Row>
                <Col md={6} className="mb-1">
                  <h6 className="text-uppercase text-secondary fw-bold small mb-1">
                    When This Happens
                  </h6>
                  <div className="fw-bold fs-6">
                    {rule.trigger?.name || rule.trigger?.description}
                  </div>
                  {renderDetails(rule.trigger?.details)}
                </Col>

                <Col md={6} className="mb-1 border-start">
                  <h6 className="text-uppercase text-secondary fw-bold small mb-1">
                    {rule.effect === "permit"
                      ? "Then Allow This"
                      : rule.effect === "deny"
                        ? "Then Deny This"
                        : "Then Execute This"}
                  </h6>
                  <div className="fw-bold fs-6">
                    {rule.action?.name || rule.action?.description}
                  </div>
                  {renderDetails(rule.action?.details)}
                </Col>
              </Row>
            </Card.Body>
          </Card>
        ))}
      </div>
    </>
  );
};

export default RuleList;
