class ConsentModel {
  uuid: string;
  content: string;
  given?: boolean;
  given_at?: string;
  sifis_action_id?: string;

  constructor(uuid: string, content: string, given?: boolean, given_at?: string, sifis_action_id?: string) {
    this.uuid = uuid;
    this.content = content;
    this.given = given;
    this.given_at = given_at;
    this.sifis_action_id = sifis_action_id;
  }
}

export { ConsentModel };
