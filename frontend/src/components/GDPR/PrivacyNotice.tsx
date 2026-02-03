import { Button, Card, CloseButton, Col, Container, Form, FormSelect, Row, ToggleButton, ToggleButtonGroup } from "react-bootstrap";
import { useState, useEffect } from "react";
import ReactQuill from "react-quill";
import {
  fetchPrivacyNoticeTemplate,
  handleSubmitPrivacyNotice,
  handleRemovePrivacyNotice,
} from "../../services/PrivacyNoticeService";
import "react-quill/dist/quill.snow.css";
import { useApp } from "../../components/AppsContext";
import { useAuth } from "../Authentication/AuthContext";
import { Role } from "../../models/user";

function PrivacyNotice(props: any) {
  const [value, setValue] = useState("");
  const [isTemplate, setIsTemplate] = useState<number>(0); // 0 = none, 1 = scratch, 2 = template
  const { loadPrivacyNotice, PrivacyNoticeByAppUUID, managedApps, selectedAppUUID, setSelectedAppUUID, loadingApps, selectedApp } = useApp();
  const { user } = useAuth();
  const [query, setQuery] = useState("");
  const closePanel = () => setSelectedAppUUID(undefined);
  const [editMode, SetEditMode] = useState(false);

  useEffect(() => {
    const setValueToTemplate = async () => {
      const template = await fetchPrivacyNoticeTemplate();
      setValue(template?.content || "");
    };
    if (isTemplate === 2) {
      setValueToTemplate();
    } else {
      setValue("");
    }
  }, [isTemplate]);



  useEffect(() => {

    if (!selectedAppUUID) return;
    void loadPrivacyNotice(selectedAppUUID, false);

  }, [loadPrivacyNotice, selectedAppUUID]);


  const pn = selectedAppUUID ? PrivacyNoticeByAppUUID[selectedAppUUID] : undefined;

  const handleSubmit = async () => {
    if (!selectedAppUUID) {
      alert("Please select an application.");
      return;
    }
    try {
      // TODO: for semplicity, we first remove any existing privacy notice before submitting a new one, REMOVE THIS!
      await handleRemovePrivacyNotice(selectedAppUUID);
      const submittedNotice = await handleSubmitPrivacyNotice(
        selectedAppUUID,
        value,
      );
      // we force the get of the new submitted
      void loadPrivacyNotice(selectedAppUUID, true)
    } catch (err) {
      console.error("Error submitting privacy notice:", err);
    }

  };

  return (
    <>
      {!loadingApps && managedApps ? (
        <>

          <Container className="py-3">

            <Row className="mb-3">
              <Col>
                <h1 className="mb-0">
                  Privacy Notices
                </h1>
              </Col>
            </Row>
            <Row className="g-3 align-items-start">
              <Col xs={12} lg={4}>
                <Container fluid className="d-flex flex-column gap-3">
                  <Card className="p-0">
                    <Card.Body>
                      <Form.Group controlId="apps-search">
                        <Form.Label className="mb-1">Search</Form.Label>
                        <Form.Control
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                          placeholder="Name, description…"
                        />
                      </Form.Group>
                    </Card.Body>
                  </Card>

                  {(managedApps.length ?? 0) === 0 ? (
                    <Card className="p-0">
                      <Card.Body className="text-muted">No managed apps.</Card.Body>
                    </Card>
                  ) : (
                    <Row xs={1} md={1} className="g-4">
                      {managedApps
                        ?.filter(
                          (app) =>
                            app.name.includes(query) ||
                            app.description?.includes(query),
                        )
                        .map((app) => {
                          const selected = app.uuid === selectedAppUUID;

                          const title =
                            app.name && app.name.trim() !== ""
                              ? app.name
                              : "Nome non impostato";
                          const vote = app.evaluation ? app.evaluation : "no vote";
                          const description = app.description;

                          return (
                            <Col key={app.uuid}>
                              <Card
                                role="button"
                                tabIndex={0}
                                onClick={() => {
                                  if (selected) {
                                    closePanel();
                                    return;
                                  }
                                  setSelectedAppUUID(app.uuid);
                                }}
                                className={[
                                  "h-100 p-0 apps_card_hover",
                                  selected ? "border-3 apps_card_selected" : "",
                                ].join(" ")}
                                style={{ cursor: "pointer" }}
                              >
                                <Card.Body>
                                  <div className="d-flex align-items-baseline gap-2">
                                    <strong>{title}</strong>
                                    <span className="text-muted">({vote})</span>
                                  </div>
                                  {description ? (
                                    <div className="text-muted">{description}</div>
                                  ) : (
                                    <div className="text-muted">
                                      (no description)
                                    </div>
                                  )}
                                  <div>
                                    <Button>
                                    Edit
                                  </Button>
                                  </div>
                                  
                                </Card.Body>
                              </Card>
                            </Col>
                          );
                        })}
                    </Row>
                  )}
                </Container>
              </Col>

              <Col xs={12} lg={8}>
                <Card className="sticky-top z-1 p-0" style={{ top: "1rem" }}>
                  <Card.Body className="d-flex flex-column gap-3">
                    {!selectedApp ? (
                      <div className="text-muted">
                        Select an app to see the PN.
                      </div>
                    ) : (
                      <>
                          <Row>
                            <Col>
                            <CloseButton onClick={closePanel} />
                            </Col>
                          </Row>
                          <Row>
                            <Row>
                              <Col>
                                <p>Choose whether to write from scratch or from a provided template:</p>
                              </Col>
                            </Row>
                            <Row>
                              <Col>
                              <ToggleButtonGroup
                                type="radio"
                                name="options"
                                defaultValue={0}
                                onChange={(val) => setIsTemplate(val)}
                              >
                                <ToggleButton id="tbg-radio-1" variant="outline-dark" value={1}>
                                  Scratch
                                </ToggleButton>
                                <ToggleButton id="tbg-radio-2" variant="outline-dark" value={2}>
                                  Template
                                </ToggleButton>
                              </ToggleButtonGroup>
                              </Col>
                              </Row>
                              {isTemplate > 0 && (
                                <div className="my-3 p-3 border rounded">
                                  <ReactQuill
                                    className="mb-3"
                                    theme="snow"
                                    value={value}
                                    onChange={setValue}
                                  />
                                  <Button variant="dark" onClick={handleSubmit} className="mt-3">
                                    Submit Privacy Notice
                                  </Button>
                                </div>
                              )}
                     
                          </Row>
                          <Row>
                            <Col>
                            <Container fluid className="ps-0">
                              {pn && pn.content && (
                                <>
                                  <h4>Contenuto Privacy Notice:</h4>
                                  <div className="mt-4 p-3 border rounded w-50">
                                    <div dangerouslySetInnerHTML={{ __html: pn.content }} />
                                  </div>
                                </>
                              )}
                            </Container>
                            </Col>
                          </Row>
                      

                      </>
                    )}
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Container>
        </>) : undefined}


      {/* <div className="d-flex flex-column align-items-center p-4">
        <h1>Privacy Notice</h1>
        <div className="w-50">
          <p>Choose a managed application to submit a privacy notice for:</p>
          <FormSelect
            className="mb-3"
            onChange={(e) => setSelectedAppUUID(e.target.value)}
            value={selectedAppUUID}
          >
            <option className="d-none" value="" disabled>
              Select an application
            </option>
            {managedApps?.map((app) => (
              <option key={app.uuid} value={app.uuid}>
                {app.name}
              </option>
            ))}
          </FormSelect>
          {user?.role != Role.DataSubject &&
            <>
              <p>Choose whether to write from scratch or from a provided template:</p>
              <ToggleButtonGroup
                type="radio"
                name="options"
                defaultValue={0}
                onChange={(val) => setIsTemplate(val)}
              >
                <ToggleButton id="tbg-radio-1" variant="outline-dark" value={1}>
                  Scratch
                </ToggleButton>
                <ToggleButton id="tbg-radio-2" variant="outline-dark" value={2}>
                  Template
                </ToggleButton>
              </ToggleButtonGroup>
              {isTemplate > 0 && (
                <div className="my-3 p-3 border rounded">
                  <ReactQuill
                    className="mb-3"
                    theme="snow"
                    value={value}
                    onChange={setValue}
                  />
                  <Button variant="dark" onClick={handleSubmit} className="mt-3">
                    Submit Privacy Notice
                  </Button>
                </div>
              )}
            </>
          }

        </div>
        {pn && pn.content && (
          <>
            <h4>Contenuto Privacy Notice:</h4>
            <div className="mt-4 p-3 border rounded w-50">
              <div dangerouslySetInnerHTML={{ __html: pn.content }} />
            </div>
          </>
        )}
      </div> */}
    </>
  );
}

export { PrivacyNotice };
