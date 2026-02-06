import {
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
import { useApp } from "../AppsContext";
import { Evaluation, Question } from "../../models/question";
import {
  fetchQuestionnaire,
  handleGetQuestionnaireByApplication,
  submitQuestionnaire,
} from "../../services/QuestionnaireService";

type Props = { closePanel: () => void; onQuestionnaireSaved?: (appUUID: string) => void };

type QuestionnaireEditorProps = Props & { questionnaireAvailable: boolean };

function QuestionnaireEditor({
  closePanel,
  onQuestionnaireSaved,
  questionnaireAvailable,
}: QuestionnaireEditorProps) {
  const { selectedAppUUID, selectedApp, reloadApps } = useApp();

  const answersRef = useRef<Record<string, string>>({});

  const [templateQuestions, setTemplateQuestions] = useState<Question[] | undefined>(
    undefined,
  );
  const [viewQuestions, setViewQuestions] = useState<Question[] | null | undefined>(
    undefined,
  );
  const [localEvaluation, setLocalEvaluation] = useState<Evaluation | undefined>(
    undefined,
  );

  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingTemplate, setLoadingTemplate] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);

  const shownEvaluation = localEvaluation ?? selectedApp?.evaluation;
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
      if (typeof questionUuid === "string" && typeof answerContent === "string") {
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
      const submitted = await submitQuestionnaire(selectedAppUUID, submissionPayload);
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
    return <div className="text-muted">Select an app to see the Questionnaire.</div>;
  }

  return (
    <>
      <Row className="align-items-start">
        <Col>
          <h3 className="mb-0 ms-1">{title}</h3>
        </Col>
        <Col xs="auto">
          <CloseButton onClick={closePanel} />
        </Col>
      </Row>

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
                    onClick={() => void handleEditClick()}
                    disabled={loading || loadingTemplate}
                  >
                    {editMode ? "Close" : hasQuestionnaire ? "Edit" : "Create"}
                  </Button>
                </Col>
                <Col xs="auto">
                  <Button type="button" variant="outline-danger" size="sm" disabled>
                    Delete
                  </Button>
                </Col>
              </Row>
              {!editMode ? (
                <Row className="mt-2">
                  <Col className="text-muted ms-2">
                    <Row className="mb-1">
                      Press {hasQuestionnaire ? "Edit" : "Create"} to{" "}
                      {hasQuestionnaire ? "update" : "submit"} the questionnaire.
                    </Row>
                    <Row>Delete not available</Row>
                  </Col>
                </Row>
              ) : null}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {error ? (
        <Card className="p-0">
          <Card.Body className="text-danger">{error}</Card.Body>
        </Card>
      ) : null}

      <Stack className="flex-grow-1 pe-2 overflow-hidden" style={{ minHeight: 0 }}>
        {loading && !editMode ? (
          <Card className="p-0">
            <Card.Body className="text-muted">Loading questionnaire…</Card.Body>
          </Card>
        ) : editMode ? (
          <Card className="p-0 flex-grow-1 overflow-hidden d-flex flex-column" style={{ minHeight: 0 }}>
            <Card.Body className="d-flex flex-column flex-grow-1" style={{ minHeight: 0 }}>
              <Row className="g-2 mb-3 align-items-center">
                <Col className="text-muted">
                  {loadingTemplate ? "Loading template…" : "Fill the questionnaire and submit it."}
                </Col>
                {shownEvaluation ? (
                  <Col xs="auto">
                    <Badge bg="light" text="dark" className="border rounded-pill">
                      {shownEvaluation}
                    </Badge>
                  </Col>
                ) : null}
              </Row>

              <div className="flex-grow-1 overflow-auto" style={{ minHeight: 0, height: 0 }}>
                {questionsToEdit.map((question, idx) => (
                  <Card key={`${question.uuid}-${selectedAppUUID || "none"}`} className="p-0 mb-3">
                    <Card.Body>
                      <Row className="g-2">
                        <Col>
                          <strong>
                            {idx + 1}. {question.content}
                          </strong>
                        </Col>
                        {question.additionalInformation ? (
                          <Col xs="auto">
                            <OverlayTrigger
                              placement="top"
                              overlay={
                                <Tooltip id={`tooltip-${question.uuid}`}>
                                  {question.additionalInformation}
                                </Tooltip>
                              }
                            >
                              <span className="text-muted" role="button">
                                i
                              </span>
                            </OverlayTrigger>
                          </Col>
                        ) : null}
                      </Row>

                      {(question.choices?.length ?? 0) > 0 ? (
                        <Form className="mt-2">
                          {question.choices?.map((choice, choiceIdx) => (
                            <Form.Check
                              key={`choice-${question.uuid}-${choiceIdx}-${selectedAppUUID || "none"}`}
                              label={choice}
                              value={choice}
                              name={`group-${question.uuid}`}
                              type="radio"
                              id={`choice-${question.uuid}-${choiceIdx}-${selectedAppUUID || "none"}`}
                              defaultChecked={answersRef.current[question.uuid] === choice}
                              onChange={(e) => saveGivenAnswer(question.uuid, e.target.value)}
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
                  disabled={loading || loadingTemplate || questionsToEdit.length === 0}
                >
                  Submit Answers
                </Button>
              </div>
            </Card.Body>
          </Card>
        ) : (
          <Card className="p-0 flex-grow-1 overflow-hidden d-flex flex-column" style={{ minHeight: 0 }}>
            <Card.Body className="d-flex flex-column flex-grow-1" style={{ minHeight: 0 }}>
              <Row className="g-1 align-items-center">
                <Col>
                  <h5 className="mb-0">Questionnaire content:</h5>
                </Col>
                {shownEvaluation ? (
                  <Col xs="auto">
                    <Badge bg="light" text="dark" className="border rounded-pill">
                      {shownEvaluation}
                    </Badge>
                  </Col>
                ) : null}
              </Row>
              <hr className="my-3" />
              <div className="flex-grow-1 overflow-auto" style={{ minHeight: 0, height: 0 }}>
                {viewQuestions === null ? (
                  <div className="text-muted">Press Create to add one</div>
                ) : viewQuestions?.length ? (
                  viewQuestions.map((question, idx) => (
                    <Card key={`${question.uuid}-${idx}`} className="p-0 mb-3">
                      <Card.Body>
                        <Row className="g-2">
                          <Col>
                            <strong>
                              {idx + 1}. {question.content}
                            </strong>
                          </Col>
                        </Row>
                        <div className="mt-2">
                          <div className="text-muted">Answer</div>
                          <div>{question.answerContent}</div>
                        </div>
                        {question.evaluation ? (
                          <div className="mt-2">
                            <div className="text-muted">Evaluation</div>
                            <div>{question.evaluation}</div>
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
