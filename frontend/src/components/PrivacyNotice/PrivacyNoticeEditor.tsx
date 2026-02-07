import { Button, Card, CloseButton, Col, Row, Stack } from "react-bootstrap";
import { useEffect, useRef, useState } from "react";
import ReactQuill from "react-quill";
import { fetchPrivacyNoticeTemplate, handleSubmitPrivacyNotice, } from "../../services/PrivacyNoticeService";
import "react-quill/dist/quill.snow.css";
import { useApp } from "../../contexts/AppsContext";
import { useAuth } from "../../contexts/AuthContext";
import { Role } from "../../models/user";

type Props = { closePanel: () => void; setPanelExpanded?: (expanded: boolean) => void };

function PrivacyNoticeEditor({ closePanel, setPanelExpanded, }: Props) {
  const [value, setValue,] = useState("");
  const { loadPrivacyNotice, PrivacyNoticeByAppUUID, selectedAppUUID, selectedApp} = useApp();
  const { user } = useAuth();

  const draftRef = useRef<string>("");
  const templateHtmlRef = useRef<string>("");
  const quillRef = useRef<ReactQuill | null>(null);
  const [editMode, setEditMode,] = useState(false);
  const pn = selectedAppUUID ? PrivacyNoticeByAppUUID[selectedAppUUID] : undefined;
  const canEdit = user?.role !== Role.DataSubject;
  const hasPn = !!(pn?.content && pn.content.trim() !== "");
  const showEmptyPn = canEdit && !editMode && !hasPn;

  useEffect(() => {
    setPanelExpanded?.(editMode);
  }, [editMode, setPanelExpanded,]);

  const ensureTemplateLoaded = async (): Promise<string> => {
    if (templateHtmlRef.current) return templateHtmlRef.current;
    const template = await fetchPrivacyNoticeTemplate();
    templateHtmlRef.current = template?.content || "";
    return templateHtmlRef.current;
  };

  useEffect(() => {
    setEditMode(false);
    setValue("");
    draftRef.current = "";
    templateHtmlRef.current = "";

    if (!selectedAppUUID) return;
    void loadPrivacyNotice(selectedAppUUID, false);
  }, [loadPrivacyNotice, selectedAppUUID,]);

  const handleSubmit = async () => {
    if (!selectedAppUUID) {
      alert("Please select an application.");
      return;
    }
    try {
      await handleSubmitPrivacyNotice(selectedAppUUID, value);
      await loadPrivacyNotice(selectedAppUUID, true);
    } catch (err) {
      //find a place where to print it
      console.error("Error submitting privacy notice:", err);
    }
  };

  const handleEditClick = () => {
    setEditMode((v) => {
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

    const merged = value ? `${value}<hr />${templateHtml}` : templateHtml;
    setValue(merged);
    draftRef.current = merged;
  };

  if (!selectedApp) {
    return (
      <div className="text-muted">
        Select an app to see the PN.
      </div>
    );
  }

  return (
    <>
      <Row className="align-items-start">
        <Col>
          <h3 className="mb-0 ms-1">
            {selectedApp?.name && selectedApp.name.trim() !== "" ? selectedApp.name : "Nome non impostato"}
          </h3>
        </Col>
        <Col xs="auto">
          <CloseButton onClick={closePanel} />
        </Col>
      </Row>

      {canEdit ? (
        <Row className="g-3">
          <Col xs={12} lg={6} xxl={5}>
            <Card className="p-0">
              <Card.Body>
                <Row className="g-2 align-items-center">
                  <Col xs="auto">
                    <strong>Actions</strong>
                  </Col>
                  <Col className="ms-auto" xs="auto">
                    <Button type="button" variant="outline-secondary" size="sm" onClick={handleEditClick}>
                      {editMode ? "Close" : hasPn ? "Edit" : "Create"}
                    </Button>
                  </Col>
                  <Col xs="auto">
                    <Button type="button" variant="outline-danger" size="sm">
                      Delete
                    </Button>
                  </Col>
                </Row>
                {!editMode ? (
                  <Row className="mt-2">
                    <Col className="text-muted ms-2">
                      <Row className="mb-1">
                        Press {hasPn ? "Edit to start editing" : "Create to create a new PN"}.
                      </Row>
                      <Row>
                        Delete is not available yet.
                      </Row>
                    </Col>
                  </Row>
                ) : null}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      ) : null}

      {showEmptyPn ? (
        <Card className="p-0">
          <Card.Body className="text-muted">
            Press Create to add one
          </Card.Body>
        </Card>
      ) : (
        <Stack className="flex-grow-1 pe-2 overflow-hidden" style={{ minHeight: 0 }}>
          {canEdit ? (
            editMode ? (
              <Card className="p-0 flex-grow-1 overflow-hidden d-flex flex-column" style={{ minHeight: 0 }}>
                <Card.Body className="d-flex flex-column flex-grow-1" style={{ minHeight: 0 }}>
                  <Row className="g-2 mb-3 align-items-center">
                    <Col className="text-muted">
                      Insert template will paste the template into your current document.
                    </Col>
                    <Col xs="auto">
                      <Button type="button" variant="outline-primary" size="sm" onClick={() => void handleInsertTemplate()}>
                        Insert template
                      </Button>
                    </Col>
                  </Row>
                  <div className="flex-grow-1 mb-3" style={{ minHeight: 0 }}>
                    <ReactQuill className="pn-quill" ref={quillRef as any} theme="snow" value={value} onChange={(html) => { setValue(html); draftRef.current = html; }} />
                  </div>
                  <div>
                    <Button variant="dark" onClick={handleSubmit}>
                      Submit Privacy Notice
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            ) : (
              <Card className="p-0">
                <Card.Body className="d-flex flex-column">
                  <Row className="g-1">
                    <Col>
                      <h5 className="mb-0">Privacy Notice content:</h5>
                    </Col>
                  </Row>
                  <hr className="my-3" />
                  <div className="overflow-auto" style={{ maxHeight: "60vh" }}>
                    <div dangerouslySetInnerHTML={{ __html: pn?.content ?? "" }} />
                  </div>
                </Card.Body>
              </Card>
            )
          ) : (
            <Card className="p-0">
              <Card.Body className="d-flex flex-column">
                <Row className="g-1">
                  <Col>
                    <h5 className="mb-0">Privacy Notice content</h5>
                  </Col>
                </Row>
                <hr className="my-3" />
                <div className="overflow-auto" style={{ maxHeight: "70vh" }}>
                  {pn?.content ? (
                    <div dangerouslySetInnerHTML={{ __html: pn.content }} />
                  ) : (
                    <div className="text-muted">
                      No Privacy Notice available.
                    </div>
                  )}
                </div>
              </Card.Body>
            </Card>
          )}
        </Stack>
      )}
    </>
  );
}

export { PrivacyNoticeEditor };
