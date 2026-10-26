import { CheckCircle2, FileText, MoreHorizontal, Plus, Sparkles, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import type { DocumentRecord } from '@/lib/api';
import type { usePdfWorkspace } from '@/hooks/use-pdf-workspace';

function DocumentList({
  documents,
  selectedId,
  onSelect,
  onDelete,
  disabled,
}: {
  disabled: boolean;
  documents: DocumentRecord[];
  selectedId: string;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  return (
    <div className="flex flex-col gap-2">
      {documents.map((document) => (
        <div
          key={document.id}
          className={`group flex items-center gap-3 rounded-lg border px-3 py-3 transition-colors ${selectedId === document.id ? "border-primary/20 bg-primary/[0.06]" : "border-transparent hover:border-border hover:bg-muted/60"}`}
        >
          <button
            disabled={disabled}
            onClick={() => onSelect(document.id)}
            className="flex min-w-0 flex-1 items-center gap-3 text-left"
            aria-pressed={selectedId === document.id}
          >
            <span className="flex size-9 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
              <FileText className="size-4" />
            </span>
            <span className="min-w-0">
              <span className="block truncate text-sm font-medium">
                {document.name}
              </span>
              <span className="mt-1 block text-xs text-muted-foreground">
                {[
                  document.pages !== undefined
                    ? `${document.pages} pages`
                    : null,
                  document.size,
                ]
                  .filter(Boolean)
                  .join(" · ") || "Saved document"}
              </span>
            </span>
          </button>
          <Button
            variant="ghost"
            size="icon"
            className="size-8 shrink-0 text-muted-foreground opacity-60 hover:text-destructive group-hover:opacity-100"
            disabled={disabled}
            onClick={() => onDelete(document.id)}
            aria-label={`Delete ${document.name}`}
          >
            <Trash2 className="size-4" />
          </Button>
        </div>
      ))}
    </div>
  );
}


export function DocumentSidebar({ documents, selectedId, selectDocument, deleteDocument,
  handleUpload, busy }: Pick<ReturnType<typeof usePdfWorkspace>,
  'documents' | 'selectedId' | 'selectDocument' | 'deleteDocument' | 'handleUpload' | 'busy'>) {
  return (<aside className="flex w-full shrink-0 flex-col border-b bg-background lg:w-[292px] lg:border-b-0 lg:border-r">
          <div className="flex items-center justify-between px-5 py-5">
            <div className="flex items-center gap-2.5">
              <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <Sparkles className="size-4" />
              </span>
              <span className="font-semibold tracking-tight">
                Atlas<span className="text-muted-foreground">/</span>pdf
              </span>
            </div>
            <Button variant="ghost" size="icon" className="size-8">
              <MoreHorizontal className="size-4" />
            </Button>
          </div>
          <Separator />
          <div className="flex flex-1 flex-col gap-5 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold">Your documents</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {documents.length} files in workspace
                </p>
              </div>
              <label htmlFor="sidebar-upload">
                <Button
                  variant="outline"
                  size="icon"
                  className="size-8"
                  aria-label="Upload PDF"
                  disabled={busy}
                  onClick={() =>
                    document.getElementById("sidebar-upload")?.click()
                  }
                >
                  <Plus className="size-4" />
                </Button>
                <input
                  id="sidebar-upload"
                  type="file"
                  accept="application/pdf"
                  className="sr-only"
                  onChange={(event) => {
                    const file = event.target.files?.[0];
                    event.target.value = '';
                    if (file) void handleUpload(file);
                  }}
                  disabled={busy}
                />
              </label>
            </div>
            <ScrollArea className="max-h-[300px] lg:max-h-none">
              <DocumentList
                documents={documents}
                selectedId={selectedId}
                onSelect={selectDocument}
                onDelete={deleteDocument}
                disabled={busy}
              />
            </ScrollArea>
            <div className="mt-auto hidden rounded-lg border bg-muted/40 p-3 lg:block">
              <div className="flex items-center gap-2 text-xs font-medium">
                <CheckCircle2 className="size-4 text-primary" /> PDF workspace
              </div>
              <p className="mt-2 text-xs leading-5 text-muted-foreground">
                Upload PDFs and ask questions about their content.
              </p>
            </div>
          </div>
        </aside>
);
}
