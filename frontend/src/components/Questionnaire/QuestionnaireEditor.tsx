import {
  Accordion,
  Button,
  Card,
  CloseButton,
  Col,
  Form,
  Row,
  Stack,
} from "react-bootstrap";
import { useCallback, useEffect, useRef, useState } from "react";
import { useApp } from "../../contexts/AppsContext";
import { Question, Questionnaire } from "../../models/question";
import {
  fetchQuestionnaire,
  submitQuestionnaire,
} from "../../services/QuestionnaireService";
import { PdfDownloadButton } from "../PdfDownloadButton";

type QuestionnaireEditorProps = {
  closePanel: () => void;
};

function QuestionnaireEditor({ closePanel }: QuestionnaireEditorProps) {
  const {
    loadQuestionnaire,
    QuestionnaireByAppUUID,
    selectedAppUUID,
    selectedApp,
  } = useApp();

  const answersRef = useRef<Record<string, string>>({});

  const [templateQuestions, setTemplateQuestions] = useState<
    Question[] | undefined
  >(undefined);

  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingTemplate, setLoadingTemplate] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);
  const questionnaire = selectedAppUUID
    ? QuestionnaireByAppUUID[selectedAppUUID]
    : undefined;
  const shownEvaluation = questionnaire?.application_evaluation;
  const shownQuestionnaireSummary = questionnaire?.questionnaire_summary;
  const viewQuestions = questionnaire?.questions;
  const hasQuestionnaire = !!shownEvaluation;

  const loadTemplateQuestions = useCallback(async () => {
    if (templateQuestions) {
      if (!hasQuestionnaire) {
        // if there is no questionnaire we want to reset the answers when opening the template
        answersRef.current = {};
      } else if (viewQuestions) {
        // if there is already a questionnaire loaded we want to seed the answers from it when opening the template
        seedAnswersFromResponse(viewQuestions);
      }
      return templateQuestions;
    }

    setLoadingTemplate(true);
    try {
      const template = await fetchQuestionnaire();
      if (!template) {
        //is a error both if is null or error in the query
        setError("Questionnaire template is empty!");
        return undefined;
      }
      setTemplateQuestions(template);
      return template;
    } catch {
      setError("Unable to load questionnaire template.");
    } finally {
      setLoadingTemplate(false);
    }
  }, [templateQuestions]);

  useEffect(() => {
    setEditMode(false);
    setError(undefined);
    setTemplateQuestions(undefined);
    answersRef.current = {};

    if (!selectedAppUUID) return;

    setLoading(true);
    loadQuestionnaire(selectedAppUUID, false)
      .then((res) => {
        if (!res) {
          return;
        }
        seedAnswersFromResponse(questionnaire?.questions ?? []);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [loadQuestionnaire, selectedAppUUID]);

  const seedAnswersFromResponse = (answeredQuestions: Question[]) => {
    answersRef.current = {};
    for (const item of answeredQuestions) {
      const questionUuid = item?.uuid;
      const answerContent = item?.answerContent;
      if (
        typeof questionUuid === "string" &&
        typeof answerContent === "string"
      ) {
        answersRef.current[questionUuid] = answerContent;
      }
    }
  };

  const handleEditClick = async () => {
    if (!selectedAppUUID) return;

    if (editMode) {
      setEditMode(false);
      return;
    }

    const template = await loadTemplateQuestions();
    if (!template) return;
    setEditMode(true);
  };

  const saveGivenAnswer = (questionUuid: string, answer: string) => {
    answersRef.current[questionUuid] = answer;
  };

  const handleSubmitAnswers = async () => {
    if (!selectedAppUUID) {
      alert("Please select an application.");
      return;
    }

    setError(undefined);
    const submissionPayload = {
      check_required: true,
      answers: Object.entries(answersRef.current).map(([key, value]) => ({
        question_uuid: key,
        answer_content: value,
      })),
    };

    setLoading(true);
    try {
      const submitted = await submitQuestionnaire(
        selectedAppUUID,
        submissionPayload,
      );
      if (!submitted) {
        setError("Error submitting the questionnaire.");
        return;
      }

      const res = await loadQuestionnaire(selectedAppUUID, true);
      if (!res) {
        setError("Questionnaire submitted, but reloading failed.");
        return;
      }
      seedAnswersFromResponse(res.questions);
      setEditMode(false);
    } finally {
      setLoading(false);
    }
  };

  const title = selectedApp?.name ?? "";

  const questionsToEdit = templateQuestions ?? [];

  return (
    <>
      <>
          <Row className="align-items-center">
            <Col className="d-flex flex-grow-1 justify-content-between align-items-center">
              <h5 className="d-inline-block mb-0 ms-1">
                Questionnaire | {title}
              </h5>
              <div className="d-flex align-items-center">
                {!editMode &&
                  selectedApp?.name &&
                  shownEvaluation &&
                  shownQuestionnaireSummary &&
                  viewQuestions?.length && (
                    <PdfDownloadButton
                      htmlContent={questionnaireObjectToHtmlString(
                        questionnaire ?? {},
                        selectedApp?.name,
                      )}
                      applicationName={title}
                      documentType="Questionnaire"
                    />
                  )}
                <Button
                  className="circular-button me-2"
                  disabled={loading || loadingTemplate}
                  style={{
                    color: "#181d1f",
                  }}
                  onClick={() => handleEditClick()}
                >
                  <i
                    className={`fa-solid fa-${editMode ? "rotate-left" : hasQuestionnaire ? "pencil" : "plus"}`}
                  ></i>
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
            </Col>
            <Col xs="auto">
              <CloseButton onClick={closePanel} />
            </Col>
          </Row>

          {error ? (
            <Card className="p-0">
              <Card.Body className="text-danger">{error}</Card.Body>
            </Card>
          ) : null}

          <Stack
            className="flex-grow-1 pe-2 overflow-hidden"
            style={{ minHeight: 0 }}
          >
            {loading && !editMode ? (
              <Card className="p-0">
                <Card.Body className="text-muted">
                  Loading questionnaire…
                </Card.Body>
              </Card>
            ) : editMode ? (
              <Card
                className="p-0 flex-grow-1 overflow-hidden d-flex flex-column"
                style={{ minHeight: 0 }}
              >
                <Card.Body
                  className="d-flex flex-column flex-grow-1"
                  style={{ minHeight: 0 }}
                >
                  <Row className="g-2 mb-3 align-items-center">
                    <Col className="text-muted">
                      {loadingTemplate
                        ? "Loading template…"
                        : "Fill the questionnaire and submit it."}
                    </Col>
                  </Row>

                  <div
                    className="flex-grow-1 overflow-auto"
                    style={{ minHeight: 0, height: 0 }}
                  >
                    {questionsToEdit.map((question, idx) => (
                      <Card
                        key={`${question.uuid}-${selectedAppUUID || "none"}`}
                        className="p-0 mb-3"
                      >
                        <Card.Body>
                          <Accordion flush key={`${question.uuid}-${idx}`}>
                            <Accordion.Item eventKey="0">
                              <Accordion.Header>
                                <h6 className="m-0">
                                  {idx + 1}. {question.content}
                                </h6>
                              </Accordion.Header>
                              <Accordion.Body>
                                {question.additionalInformation}
                              </Accordion.Body>
                            </Accordion.Item>
                          </Accordion>
                          {(question.choices?.length ?? 0) > 0 ? (
                            <Form className="mt-2">
                              {question.choices?.map((choice, choiceIdx) => (
                                <Form.Check
                                  inline
                                  key={`choice-${question.uuid}-${choiceIdx}-${selectedAppUUID || "none"}`}
                                  label={choice}
                                  value={choice}
                                  name={`group-${question.uuid}`}
                                  type="radio"
                                  id={`choice-${question.uuid}-${choiceIdx}-${selectedAppUUID || "none"}`}
                                  defaultChecked={
                                    answersRef.current[question.uuid] === choice
                                  }
                                  onChange={(e) =>
                                    saveGivenAnswer(
                                      question.uuid,
                                      e.target.value,
                                    )
                                  }
                                />
                              ))}
                            </Form>
                          ) : (
                            <div className="text-muted mt-2">(no choices)</div>
                          )}
                        </Card.Body>
                      </Card>
                    ))}
                  </div>

                  <div className="mt-3">
                    <Button
                      variant="dark"
                      onClick={() => void handleSubmitAnswers()}
                      disabled={
                        loading ||
                        loadingTemplate ||
                        questionsToEdit.length === 0
                      }
                    >
                      Submit Answers
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            ) : (
              <Card
                className="p-0 flex-grow-1 overflow-hidden d-flex flex-column"
                style={{ minHeight: 0 }}
              >
                <Card.Body
                  className="d-flex flex-column flex-grow-1"
                  style={{ minHeight: 0 }}
                >
                  {shownEvaluation && shownQuestionnaireSummary && (
                    <Row className="g-1 align-items-center">
                      <p>
                        <strong>{selectedApp?.name}</strong> got the following
                        evaluation:{" "}
                        <span
                          style={{
                            color: shownEvaluation.toLowerCase(),
                            fontWeight: "bold",
                          }}
                        >
                          {shownEvaluation}
                        </span>
                      </p>
                      <p>{shownQuestionnaireSummary}</p>
                      <hr className="my-3" />
                    </Row>
                  )}
                  <div
                    className="flex-grow-1 overflow-auto"
                    style={{ minHeight: 0, height: 0 }}
                  >
                    {viewQuestions === null ? (
                      <div className="text-muted">
                        Press the Plus button to fill out the questionnaire.
                      </div>
                    ) : viewQuestions?.length ? (
                      viewQuestions.map((question, idx) => (
                        <Card
                          key={`${question.uuid}-${idx}`}
                          className="p-0 mb-3"
                        >
                          <Card.Body>
                            <Accordion flush key={`${question.uuid}-${idx}`}>
                              <Accordion.Item eventKey="0">
                                <Accordion.Header>
                                  <h6 className="m-0">
                                    {idx + 1}. {question.content}
                                  </h6>
                                </Accordion.Header>
                                <Accordion.Body>
                                  {question.additionalInformation}
                                </Accordion.Body>
                              </Accordion.Item>
                            </Accordion>
                            <div className="mt-2">
                              <div className="text-muted">Answer</div>
                              <div>{question.answerContent}</div>
                            </div>
                            {question.evaluation ? (
                              <div className="mt-2">
                                <div className="text-muted">Evaluation</div>
                                <div
                                  style={{
                                    color: question.evaluation.toLowerCase(),
                                    fontWeight: "bold",
                                  }}
                                >
                                  {question.evaluation}
                                </div>
                              </div>
                            ) : null}
                          </Card.Body>
                        </Card>
                      ))
                    ) : (
                      <div className="text-muted">
                        No questionnaire available.
                      </div>
                    )}
                  </div>
                </Card.Body>
              </Card>
              )}
            </Stack>
          </>
    </>
  );
}

function questionnaireObjectToHtmlString(
  obj: Questionnaire,
  applicationName: string,
): string {
  return `<p><strong>${applicationName}</strong> got the following evaluation: <span style="font-weight: bold; color: ${obj.application_evaluation?.toLowerCase()};">${obj.application_evaluation}</span></p><p>${obj.questionnaire_summary ?? ""}</p><hr/><div>${obj.questions
    .map(
      (question, idx) =>
        `<div key=${question.uuid}><p><strong>${idx + 1}. ${question.content}</strong></p><p><i>${question.additionalInformation ?? ""}</i></p><p><strong>Answer:</strong> ${question.answerContent ?? "No answer given"}</p><p><strong>Evaluation:</strong> <span style="font-weight: bold; color: ${question.evaluation?.toLowerCase()};">${question.evaluation ?? "No evaluation"}</span></p></div>`,
    )
    .join("")}</div>`;
}

export { QuestionnaireEditor };
