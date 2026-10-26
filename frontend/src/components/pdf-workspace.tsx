import { Badge } from '@/components/ui/badge';
import { usePdfWorkspace } from '@/hooks/use-pdf-workspace';
import { DocumentSidebar } from './pdf-workspace/document-sidebar';
import { PdfUploadCard } from './pdf-workspace/pdf-upload-card';
import { QuestionCard } from './pdf-workspace/question-card';
import { AnswerPanel } from './pdf-workspace/answer-panel';

// Compose the page; state and individual sections live in their own files.
export function PdfWorkspace() {
  const workspace = usePdfWorkspace();

  return (
    <main className="min-h-screen bg-muted/30 text-foreground">
      <div className="mx-auto flex min-h-screen max-w-[1440px] flex-col lg:flex-row">
        <DocumentSidebar {...workspace} />
        <section className="flex min-w-0 flex-1 flex-col">
          <header className="flex items-center justify-between border-b bg-background px-5 py-4 sm:px-8">
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
                Document workspace
              </p>
              <h1 className="mt-1 text-lg font-semibold tracking-tight">Ask your PDFs</h1>
            </div>
            <Badge variant="secondary" className="gap-1.5 font-normal">
              <span className="size-1.5 rounded-full bg-emerald-500" /> Ready
            </Badge>
          </header>
          <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-6 p-5 sm:p-8 lg:p-12">
            <div role="status" aria-live="polite">
              {workspace.loadingDocuments && <p className="text-sm text-muted-foreground">Loading documents...</p>}
              {workspace.uploading && <p className="text-sm text-muted-foreground">Uploading and processing PDF...</p>}
              {workspace.deleting && <p className="text-sm text-muted-foreground">Deleting document...</p>}
            </div>
            <PdfUploadCard disabled={workspace.busy} onUpload={workspace.handleUpload}
              onError={workspace.reportUploadError} />
            <QuestionCard {...workspace} />
            <AnswerPanel {...workspace} />
          </div>
        </section>
      </div>
    </main>
  );
}
