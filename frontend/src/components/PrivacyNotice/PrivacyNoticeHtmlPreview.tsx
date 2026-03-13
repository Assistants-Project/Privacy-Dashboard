import { Spinner } from "react-bootstrap";
import type { CSSProperties } from "react";
import sanitizeHtml from "./sanitizeHtml";

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
  const safe = sanitizeHtml(normalized);
  const hasContent = safe !== "";

  return (
    <div
      className={["border", "border-2", "rounded-4", "p-3", "overflow-auto", className].filter(Boolean).join(" ")}
      style={{ maxHeight: maxHeight ?? "60vh", ...style }}
    >
      {hasContent ? (
        <div
          className="ql-editor p-0"
          style={{ padding: 0, overflowY: "visible", height: "auto" }}
          dangerouslySetInnerHTML={{ __html: safe }}
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
