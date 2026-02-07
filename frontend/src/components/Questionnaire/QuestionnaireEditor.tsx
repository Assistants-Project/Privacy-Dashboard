import {
  Accordion,
  Badge,
  Button,
  Card,
  CloseButton,
  Col,
  Form,
  OverlayTrigger,
  Row,
  Stack,
  Tooltip,
} from "react-bootstrap";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useApp } from "../../contexts/AppsContext";
import { Evaluation, Question } from "../../models/question";
import {
  fetchQuestionnaire,
  handleGetQuestionnaireByApplication,
  submitQuestionnaire,
} from "../../services/QuestionnaireService";

type Props = {
  closePanel: () => void;
  onQuestionnaireSaved?: (appUUID: string) => void;
};

type QuestionnaireEditorProps = Props & { questionnaireAvailable: boolean };

function QuestionnaireEditor({
  closePanel,
  onQuestionnaireSaved,
  questionnaireAvailable,
}: QuestionnaireEditorProps) {
  const { selectedAppUUID, selectedApp, reloadApps } = useApp();

  const answersRef = useRef<Record<string, string>>({});

  const [templateQuestions, setTemplateQuestions] = useState<
    Question[] | undefined
  >(undefined);
  const [viewQuestions, setViewQuestions] = useState<
    Question[] | null | undefined
  >(undefined);
  const [localEvaluation, setLocalEvaluation] = useState<
    Evaluation | undefined
  >(undefined);
  const [localQuestionnaireSummary, setLocalQuestionnaireSummary] = useState<
    string | undefined
  >(undefined);

  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingTemplate, setLoadingTemplate] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);

  const shownEvaluation = localEvaluation ?? selectedApp?.evaluation;
  const shownQuestionnaireSummary =
    localQuestionnaireSummary ?? selectedApp?.questionnaire_summary;
  const hasQuestionnaire = !!shownEvaluation;

  const loadTemplateQuestions = useCallback(async () => {
    if (templateQuestions) return templateQuestions;

    setLoadingTemplate(true);
    try {
      const template = await fetchQuestionnaire();
      if (!template) {
        setError("Unable to load questionnaire template.");
        return undefined;
      }
      setTemplateQuestions(template);
      return template;
    } finally {
      setLoadingTemplate(false);
    }
  }, [templateQuestions]);

  const mapQuestionnaireResponseToQuestions = (res: any): Question[] => {
    const given = Array.isArray(res?.given_answers) ? res.given_answers : [];
    return given.map(
      (q: any) =>
        ({
          uuid: q.question.uuid,
          content: q.question.content,
          additionalInformation: q.question.additional_information,
          answerContent: q.answer.answer_content,
          evaluation: q.answer.evaluation,
        }) as Question,
    );
  };

  const seedAnswersFromResponse = (res: any) => {
    answersRef.current = {};
    const given = Array.isArray(res?.given_answers) ? res.given_answers : [];
    for (const item of given) {
      const questionUuid = item?.question?.uuid;
      const answerContent = item?.answer?.answer_content;
      if (
        typeof questionUuid === "string" &&
        typeof answerContent === "string"
      ) {
        answersRef.current[questionUuid] = answerContent;
      }
    }
  };

  // Load current questionnaire (view mode) when selecting an app.
  useEffect(() => {
    setEditMode(false);
    setError(undefined);
    setTemplateQuestions(undefined);
    setViewQuestions(undefined);
    setLocalEvaluation(undefined);
    setLocalQuestionnaireSummary(undefined);
    answersRef.current = {};

    if (!selectedAppUUID) return;

    if (!questionnaireAvailable) {
      setViewQuestions(null);
      return;
    }

    setLoading(true);
    void handleGetQuestionnaireByApplication(selectedAppUUID)
      .then((res) => {
        if (!res) {
          setError("Unable to load the questionnaire.");
          setViewQuestions(undefined);
          return;
        }
        setLocalEvaluation(res.application_evaluation);
        setLocalQuestionnaireSummary(res.questionnaire_summary);
        setViewQuestions(mapQuestionnaireResponseToQuestions(res));
        seedAnswersFromResponse(res);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [questionnaireAvailable, selectedAppUUID]);

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
    if (!selectedAppUUID) return;

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

      const res = await handleGetQuestionnaireByApplication(selectedAppUUID);
      if (!res) {
        setError("Questionnaire submitted, but reloading failed.");
        return;
      }

      reloadApps();
      setLocalEvaluation(res.application_evaluation);
      setLocalQuestionnaireSummary(res.questionnaire_summary);
      setViewQuestions(mapQuestionnaireResponseToQuestions(res));
      seedAnswersFromResponse(res);
      setEditMode(false);
      onQuestionnaireSaved?.(selectedAppUUID);
    } finally {
      setLoading(false);
    }
  };

  const title =
    selectedApp?.name && selectedApp.name.trim() !== ""
      ? selectedApp.name
      : "Nome non impostato";

  const questionsToEdit = templateQuestions ?? [];

  if (!selectedApp) {
    return (
      <div className="text-muted">Select an app to see the Questionnaire.</div>
    );
  }

  return (
    <>
      <Row className="align-items-center">
        <Col className="d-flex flex-grow-1 justify-content-between align-items-center">
          <h3 className="d-inline-block mb-0 ms-1">{title}</h3>
          <div className="d-flex align-items-center">
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
            <Card.Body className="text-muted">Loading questionnaire…</Card.Body>
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
                                saveGivenAnswer(question.uuid, e.target.value)
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
                    loading || loadingTemplate || questionsToEdit.length === 0
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
                    <strong>{selectedApp.name}</strong> got the following
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
                </Row>
              )}
              <hr className="my-3" />
              <div
                className="flex-grow-1 overflow-auto"
                style={{ minHeight: 0, height: 0 }}
              >
                {viewQuestions === null ? (
                  <div className="text-muted">
                    Press the Plus button to start the questionnaire.
                  </div>
                ) : viewQuestions?.length ? (
                  viewQuestions.map((question, idx) => (
                    <Card key={`${question.uuid}-${idx}`} className="p-0 mb-3">
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
                  <div className="text-muted">No questionnaire available.</div>
                )}
              </div>
            </Card.Body>
          </Card>
        )}
      </Stack>
    </>
  );
}

export { QuestionnaireEditor };
