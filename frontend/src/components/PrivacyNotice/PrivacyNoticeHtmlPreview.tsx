import { Spinner } from "react-bootstrap";

type Props = {
  content?: string | null;
  loading?: boolean;
  emptyText?: string;
  maxHeight?: string | number;
};

function PrivacyNoticeHtmlPreview({ content, loading, emptyText, maxHeight }: Props) {
  const normalized = typeof content === "string" ? content.trim() : "";
  const hasContent = normalized !== "";

  return (
    <div className="border rounded p-2 overflow-auto" style={{ maxHeight: maxHeight ?? "60vh" }}>
      {hasContent ? (
        <div dangerouslySetInnerHTML={{ __html: normalized }} />
      ) : loading ? (
        <div className="d-inline-flex align-items-center gap-2 text-muted small">
          <Spinner animation="border" size="sm" /> Loading…
        </div>
      ) : (
        <div className="text-muted small">{emptyText ?? "No Privacy Notice available"}</div>
      )}
    </div>
  );
}

export { PrivacyNoticeHtmlPreview };

