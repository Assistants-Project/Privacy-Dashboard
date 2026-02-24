function collectValidationMessages(value: unknown): string[] {
  if (typeof value === "string") {
    return [value];
  }
  if (Array.isArray(value)) {
    return value.flatMap(collectValidationMessages);
  }
  if (value && typeof value === "object") {
    return Object.values(value as Record<string, unknown>).flatMap(collectValidationMessages);
  }
  return [];
}

export async function getApiError(
  response: Response,
  fallbackMessage = "Something went wrong",
): Promise<Error> {
  try {
    const errDetail: any = await response.json();

    // Flask-smorest validation error
    if (errDetail?.errors) {
      if (typeof errDetail.errors === "string") {
        return new Error(errDetail.errors);
      }
      const messages = collectValidationMessages(errDetail.errors);
      if (messages.length > 0) {
        return new Error(messages.join("\n"));
      }
    }

    if (errDetail?.message) return new Error(errDetail.message);
    if (errDetail?.error) return new Error(errDetail.error);
  } catch {
    // ignore parsing errors and fall back
  }

  return new Error(fallbackMessage);
}
