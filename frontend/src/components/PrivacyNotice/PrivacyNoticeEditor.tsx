import { Button, Card, CloseButton, Col, Row, Stack } from "react-bootstrap";
import { useEffect, useRef, useState } from "react";
import ReactQuill from "react-quill";
import { fetchPrivacyNoticeTemplate, handleSubmitPrivacyNotice, } from "../../services/PrivacyNoticeService";
import "react-quill/dist/quill.snow.css";
import { useApp } from "../../contexts/AppsContext";
import { useAuth } from "../../contexts/AuthContext";
import { PdfDownloadButton } from "../Utilities/PdfDownloadButton";
import { ApplyExistingPrivacyNoticeModal } from "./ApplyExistingPrivacyNoticeModal";
import { PrivacyNoticeHtmlPreview } from "./PrivacyNoticeHtmlPreview";

type Props = { closePanel: () => void; setPanelExpanded?: (expanded: boolean) => void };

function PrivacyNoticeEditor({ closePanel, setPanelExpanded, }: Props) {
  const [value, setValue,] = useState("");
  const { loadPrivacyNotice, PrivacyNoticeByAppUUID, selectedAppUUID, selectedApp} = useApp();
  const { user, isDataSubject } = useAuth();
  const [showApplyExistingModal, setShowApplyExistingModal] = useState(false);

  const draftRef = useRef<string>("");
  const templateHtmlRef = useRef<string>("");
  const quillRef = useRef<ReactQuill | null>(null);
  const [editMode, setEditMode,] = useState(false);
  const pn = selectedAppUUID ? PrivacyNoticeByAppUUID[selectedAppUUID] : undefined;
  const hasPn = !!(pn?.content && pn.content.trim() !== "");
  const showEmptyPn = !isDataSubject && !editMode && !hasPn;

  useEffect(() => {
    setPanelExpanded?.(editMode);
  }, [editMode, setPanelExpanded]);

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
  }, [loadPrivacyNotice, selectedAppUUID]);

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
    if (editMode) {
      setEditMode(false);
      return;
    }

    // Reset editor content: if no PN loaded, clear editor; otherwise restore PN content.
    const editor = (quillRef.current as any)?.getEditor?.();

    if (!hasPn) {
      if (editor) {
        try {
          editor.setContents([]);
        } catch (e) {
          if (editor.root) editor.root.innerHTML = "";
        }
      }
      setValue("");
      draftRef.current = "";
    } else {
      // Restore the fetched privacy notice content
      const content = pn?.content ?? "";
      if (editor) {
        editor.clipboard?.dangerouslyPasteHTML(0, content);
      }
      setValue(content);
      draftRef.current = content;
    }
    setEditMode(true);
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

  const title = selectedApp?.name ?? "";

  return (
    <>
      <Row className="align-items-center">
        <Col className="d-flex flex-grow-1 justify-content-between align-items-center">
          <h5 className="d-inline-block mb-0 ms-1">Privacy Notice | {title}</h5>
          {!isDataSubject ? (
            <div className="d-flex align-items-center">
              {hasPn && !editMode && (
                <PdfDownloadButton
                  htmlContent={pn?.content ?? ""}
                  applicationName={title}
                  documentType="Privacy Notice"
                />
              )}
              <Button
                className="circular-button me-2"
                style={{
                  color: "#181d1f",
                }}
                onClick={() => handleEditClick()}
              >
                <i
                  className={`fa-solid fa-${editMode ? "rotate-left" : hasPn ? "pencil" : "plus"}`}
                ></i>
              </Button>
              <Button
                className="circular-button me-2"
                style={{ color: "#181d1f" }}
                disabled={!selectedAppUUID}
                onClick={() => setShowApplyExistingModal(true)}
                title="Apply existing Privacy Notice"
              >
                <i className="fa-solid fa-right-left"></i>
              </Button>
              <Button
                className="circular-button"
                disabled
                style={{
                  color: "red",
                }}
              >
                <i className="fa-solid fa-trash"></i>
              </Button>
            </div>
          ) : (
            hasPn && (
              <PdfDownloadButton
                htmlContent={pn?.content ?? ""}
                applicationName={title}
                documentType="Privacy Notice"
              />
            )
          )}
        </Col>
        <Col xs="auto">
          <CloseButton onClick={closePanel} />
        </Col>
      </Row>

          {showEmptyPn ? (
            <Card className="p-0">
              <Card.Body className="text-muted">
            {!isDataSubject
              ? "Press the Plus button to start writing the Privacy Notice."
              : "No Privacy Notice available."}
              </Card.Body>
            </Card>
          ) : (
        <Stack
          className="flex-grow-1 pe-2 overflow-hidden"
          style={{ minHeight: 0 }}
        >
          {!isDataSubject ? (
            editMode ? (
              <Card
                className="p-0 flex-grow-1 overflow-hidden d-flex flex-column"
                style={{ minHeight: 0 }}
              >
                <Card.Body
                  className="d-flex flex-column flex-grow-1"
                  style={{ minHeight: 0 }}
                >
                  <div
                    className="flex-grow-1 mb-3 position-relative"
                    style={{ minHeight: 0 }}
                  >
                    <ReactQuill
                      className="pn-quill"
                      ref={quillRef as any}
                      theme="snow"
                      value={value}
                      onChange={(html) => {
                        setValue(html);
                        draftRef.current = html;
                      }}
                    />
                    <button
                      type="button"
                      className="btn btn-sm insert-template-btn"
                      onClick={() => void handleInsertTemplate()}
                    >
                      <strong>Insert Template</strong>
                    </button>
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
                  <PrivacyNoticeHtmlPreview content={pn?.content} maxHeight="60vh" />
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
                <PrivacyNoticeHtmlPreview content={pn?.content} maxHeight="70vh" />
              </Card.Body>
            </Card>
          )}
        </Stack>
      )}
      {!isDataSubject && (
        <ApplyExistingPrivacyNoticeModal
          show={showApplyExistingModal}
          onHide={() => setShowApplyExistingModal(false)}
        />
      )}
    </>
  );
}

export { PrivacyNoticeEditor };
