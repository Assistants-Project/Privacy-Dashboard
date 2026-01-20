export interface Question {
  uuid: string;
  content: string;
  additionalInformation?: string;
  choices?: string[];
  answerContent?: string;
  evaluation?: Evaluation;
}

export enum Evaluation {
  GREEN = "GREEN",
  ORANGE = "ORANGE",
  RED = "RED",
}
