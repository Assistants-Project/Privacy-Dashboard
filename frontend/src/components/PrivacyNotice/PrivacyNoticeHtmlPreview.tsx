import { Spinner } from "react-bootstrap";
import type { CSSProperties } from "react";

type Props = {
  content?: string | null;
  loading?: boolean;
  emptyText?: string;
  maxHeight?: string | number;
  className?: string;
  style?: CSSProperties;
};

function PrivacyNoticeHtmlPreview({ content, loading, emptyText, maxHeight, className, style }: Props) {
  const normalized = typeof content === "string" ? content.trim() : "";
  const hasContent = normalized !== "";

  return (
    <div
      className={["border rounded p-2 overflow-auto", className].filter(Boolean).join(" ")}
      style={{ maxHeight: maxHeight ?? "60vh", ...style }}
    >
      {hasContent ? (
        <div
          className="ql-editor p-0"
          style={{ padding: 0, overflowY: "visible", height: "auto" }}
          dangerouslySetInnerHTML={{ __html: normalized }}
        />
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
