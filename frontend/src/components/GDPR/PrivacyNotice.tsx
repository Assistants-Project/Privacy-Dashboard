import { Button, Card, CloseButton, Col, Container, Form, Row, Stack } from "react-bootstrap";
import { useEffect, useRef, useState } from "react";
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
  const { loadPrivacyNotice, PrivacyNoticeByAppUUID, managedApps, selectedAppUUID, setSelectedAppUUID, loadingApps, selectedApp } = useApp();
  const { user } = useAuth();
  const [query, setQuery] = useState("");
  const draftRef = useRef<string>("");
  const templateHtmlRef = useRef<string>("");
  const quillRef = useRef<ReactQuill | null>(null);
  const [editMode, SetEditMode] = useState(false);
  const pn = selectedAppUUID ? PrivacyNoticeByAppUUID[selectedAppUUID] : undefined;
  const canEdit = user?.role !== Role.DataSubject;
  const hasPn = !!(pn?.content && pn.content.trim() !== "");

  const ensureTemplateLoaded = async (): Promise<string> => {
    if (templateHtmlRef.current) return templateHtmlRef.current;
    const template = await fetchPrivacyNoticeTemplate();
    templateHtmlRef.current = template?.content || "";
    return templateHtmlRef.current;
  };

  const closePanel = () => {
    setSelectedAppUUID(undefined);
    SetEditMode(false);
    setValue("");
    draftRef.current = "";
    templateHtmlRef.current = "";
  };

  useEffect(() => {

    if (!selectedAppUUID) return;
    SetEditMode(false);
    setValue("");
    draftRef.current = "";
    templateHtmlRef.current = "";
    void loadPrivacyNotice(selectedAppUUID, false);

  }, [loadPrivacyNotice, selectedAppUUID]);

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



  const handleEditClick = () => {
    SetEditMode((v) => {
      const next = !v;
      if (next) {
        templateHtmlRef.current = "";
        if (!draftRef.current) draftRef.current = pn?.content || "";
        setValue(draftRef.current);
      } else {
        draftRef.current = value;
        setValue("");
      }
      return next;
    });
  };

  const handleInsertTemplate = async () => {
    const templateHtml = await ensureTemplateLoaded();
    if (!templateHtml) return;

    const editor = (quillRef.current as any)?.getEditor?.();
    if (editor) {
      const selection = editor.getSelection?.();
      const index = selection?.index ?? editor.getLength?.() ?? 0;
      editor.clipboard?.dangerouslyPasteHTML(index, templateHtml);
      const nextHtml = editor.root?.innerHTML;
      if (typeof nextHtml === "string") {
        setValue(nextHtml);
        draftRef.current = nextHtml;
      }
      return;
    }

    const merged = value
      ? `${value}<hr />${templateHtml}`
      : templateHtml;
    setValue(merged);
    draftRef.current = merged;
  };

  return (
    <>
      {!loadingApps && managedApps ? (
        <>

          <Container fluid className="py-3 ps-5 pe-5">

            <Row className="mb-3">
              <Col>
                <h1 className="mb-0">
                  Privacy Notices
                </h1>
              </Col>
            </Row>
            <Row className="g-3 align-items-start">
              <Col xs={3} lg={3}>
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
                    <Stack
                      className="overflow-auto pe-3"
                      style={{ maxHeight: "calc(100vh - 12rem)" }}
                    >
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
                                    </div>
                                    {description ? (
                                      <div className="text-muted">{description}</div>
                                    ) : (
                                      <div className="text-muted">(no description)</div>
                                    )}
                                  </Card.Body>
                                </Card>
                              </Col>
                            );
                          })}
                      </Row>
                    </Stack>
                  )}
                </Container>
              </Col>

              <Col xs={9} lg={9}>
                <Card
                  className="sticky-top z-1 p-0 overflow-hidden"
                  style={{ top: "1rem", maxHeight: "calc(100vh - 2rem)" }}
                >
                  <Card.Body className="d-flex flex-column gap-3" style={{ minHeight: 0 }}>
                    {!selectedApp ? (
                      <div className="text-muted">
                        Select an app to see the PN.
                      </div>
                    ) : (
                      <>
                        <Row className="align-items-start">
                          <Col>
                            <h3 className="mb-0 ms-1">
                              {selectedApp?.name && selectedApp.name.trim() !== ""
                                ? selectedApp.name
                                : "Nome non impostato"}
                            </h3>
                          </Col>
                          <Col xs="auto">
                            <CloseButton onClick={closePanel} />
                          </Col>
                        </Row>

                        {canEdit ? (
                          <>
                            <Row className="g-3">
                              <Col xs={12} lg={6} xxl={5}>
                                <Card className="p-0">
                                  <Card.Body>
                                    <Row className="g-2 align-items-center">
                                      <Col xs="auto">
                                        <strong>Actions</strong>
                                      </Col>
                                      <Col className="ms-auto" xs="auto">
                                        <Button
                                          type="button"
                                          variant="outline-secondary"
                                          size="sm"
                                          onClick={handleEditClick}
                                        >
                                          {editMode ? "Close" : hasPn ? "Edit" : "Create"}
                                        </Button>
                                      </Col>
                                      <Col xs="auto">
                                        <Button
                                          type="button"
                                          variant="outline-danger"
                                          size="sm"
                                        >
                                          Delete
                                        </Button>
                                      </Col>
                                    </Row>
                                    {!editMode ? (
                                      <Row className="mt-2">
                                        <Col className="text-muted ms-2">
                                          <Row className="mb-1">
                                            Press {hasPn ? "Edit" : "Create"} to start editing.
                                          </Row>
                                          <Row>
                                            Press Delete to delete the Privacy Notice.
                                          </Row>

                                        </Col>

                                      </Row>
                                    ) : null}
                                  </Card.Body>
                                </Card>
                              </Col>
                            </Row>
                          </>
                        ) : null}

                        <Stack className="flex-grow-1 overflow-auto pe-2" style={{ minHeight: 0 }}>
                          {canEdit ? (
                            editMode ? (
                              <Card className="p-0">
                                <Card.Body>
                                  <Row className="g-2 mb-3 align-items-center">
                                    <Col className="text-muted">
                                      Insert template will paste the template into your current document.
                                    </Col>
                                    <Col xs="auto">
                                      <Button
                                        type="button"
                                        variant="outline-primary"
                                        size="sm"
                                        onClick={() => void handleInsertTemplate()}
                                      >
                                        Insert template
                                      </Button>
                                    </Col>
                                  </Row>
                                  <ReactQuill
                                    className="mb-3"
                                    ref={quillRef as any}
                                    theme="snow"
                                    value={value}
                                    onChange={(html) => {
                                      setValue(html);
                                      draftRef.current = html;
                                    }}
                                  />
                                  <Button variant="dark" onClick={handleSubmit}>
                                    Submit Privacy Notice
                                  </Button>
                                </Card.Body>
                              </Card>
                            ) : (
                              <Card className="p-0">
                                <Card.Body>
                                  <Row className="g-1">
                                    <Col>
                                      <h5 className="mb-0">Privacy Notice content:</h5>
                                    </Col>
                                  </Row>
                                  <hr className="my-3" />
                                  {pn?.content ? (
                                    <div dangerouslySetInnerHTML={{ __html: pn.content }} />
                                  ) : (
                                    <div className="text-muted">
                                      No Privacy Notice yet. Press Create to add one.
                                    </div>
                                  )}
                                </Card.Body>
                              </Card>
                            )
                          ) : (
                            <Card className="p-0">
                              <Card.Body>
                                <Row className="g-1">
                                  <Col>
                                    <h5 className="mb-0">Privacy Notice content</h5>
                                  </Col>
                                </Row>
                                <hr className="my-3" />
                                {pn?.content ? (
                                  <div dangerouslySetInnerHTML={{ __html: pn.content }} />
                                ) : (
                                  <div className="text-muted">No Privacy Notice available.</div>
                                )}
                              </Card.Body>
                            </Card>
                          )}
                        </Stack>


                      </>
                    )}
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Container>
        </>) : undefined}
    </>
  );
}

export { PrivacyNotice };
