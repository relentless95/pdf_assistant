import { useMemo, useState, useEffect } from 'react';
import { listDocuments, uploadPdf, askQuestion, deleteSavedDocument,
  type DocumentRecord, type SourceExcerpt } from '@/lib/api';

// Own the workspace state and API requests; components handle presentation.
export function usePdfWorkspace() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [question, setQuestion] = useState("");

  const [status, setStatus] = useState<
    "empty" | "loading" | "success" | "error" | "insufficient"
  >("empty");

  const [answer, setAnswer] = useState<{
    text: string;
    sources: SourceExcerpt[];
  } | null>(null);

  const [error, setError] = useState("");
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const busy =
    loadingDocuments || uploading || deleting || status === "loading";

  const selectedDocument = useMemo(
    () => documents.find((document) => document.id === selectedId),
    [documents, selectedId],
  );

  useEffect(() => {
    let active = true;

    async function loadDocuments() {
      try {
        const savedDocuments = await listDocuments();

        if (!active) return;

        setDocuments(savedDocuments);
        setSelectedId(savedDocuments[0]?.id ?? "");
      } catch (caught) {
        if (!active) return;

        setError(
          caught instanceof Error
            ? caught.message
            : "Could not load documents.",
        );
        setStatus("error");
      } finally {
        if (active) setLoadingDocuments(false);
      }
    }

    void loadDocuments();

    return () => {
      active = false;
    };
  }, []);

  function resetAnswer() {
    setAnswer(null);
    setError("");
    setStatus("empty");
  }

  function selectDocument(id: string) {
    if (busy) return;

    setSelectedId(id);
    resetAnswer();
  }

  async function handleUpload(file: File) {
    if (busy) return;

    resetAnswer();

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      reportUploadError('Choose a PDF file.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("Choose a PDF no larger than 10 MiB.");
      setStatus("error");
      return;
    }

    setUploading(true);

    try {
      const uploadedDocument = await uploadPdf(file);

      setDocuments((current) => [uploadedDocument, ...current]);
      setSelectedId(uploadedDocument.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Upload failed.");
      setStatus("error");
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk() {
    if (busy) return;

    const trimmedQuestion = question.trim();

    if (!selectedId || !trimmedQuestion) {
      setError("Select a document and enter a question.");
      setStatus("error");
      return;
    }

    setAnswer(null);
    setError("");
    setStatus("loading");

    try {
      const result = await askQuestion(selectedId, trimmedQuestion);

      if (result.insufficientEvidence) {
        setStatus("insufficient");
        return;
      }

      setAnswer({
        text: result.text,
        sources: result.sources,
      });
      setStatus("success");
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Could not answer the question.",
      );
      setStatus("error");
    }
  }

  async function deleteDocument(id: string) {
    if (busy) return;

    setDeleting(true);

    try {
      await deleteSavedDocument(id);

      const remaining = documents.filter((document) => document.id !== id);

      setDocuments(remaining);

      if (selectedId === id) {
        setSelectedId(remaining[0]?.id ?? "");
        resetAnswer();
      }
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Could not delete the document.",
      );
      setStatus("error");
    } finally {
      setDeleting(false);
    }
  }

  function reportUploadError(message: string) {
    if (busy) return;
    setAnswer(null);
    setError(message);
    setStatus('error');
  }

  return {
    documents, selectedId, question, setQuestion, status, setStatus,
    answer, error, loadingDocuments, uploading, deleting, busy,
    selectedDocument, selectDocument, handleUpload, handleAsk,
    deleteDocument, reportUploadError,
  };
}
