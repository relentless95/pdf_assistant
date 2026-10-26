import { useState } from 'react';
import { AlertCircle, FolderOpen } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { SourceExcerpt } from '@/lib/api';
import type { usePdfWorkspace } from '@/hooks/use-pdf-workspace';

function SourceItem({ source }: { source: SourceExcerpt }) {
  const [open, setOpen] = useState(false);
  return (
    <button
      className="w-full rounded-lg border bg-background p-3 text-left transition-colors hover:bg-muted/40"
      onClick={() => setOpen(!open)}
      aria-expanded={open}
    >
      <span className="flex items-center justify-between gap-4">
        <span className="flex items-center gap-2 text-sm font-medium">
          <span className="flex size-6 items-center justify-center rounded bg-muted text-xs text-muted-foreground">
            {source.page}
          </span>
          Page {source.page}
        </span>
        <span className="text-xs text-muted-foreground">
          {open ? "Hide excerpt" : "View excerpt"}
        </span>
      </span>
      {open && (
        <span className="mt-3 block border-t pt-3 text-sm leading-6 text-muted-foreground">
          “{source.excerpt}”
        </span>
      )}
    </button>
  );
}


export function AnswerPanel({ status, setStatus, answer, error, selectedDocument }:
  Pick<ReturnType<typeof usePdfWorkspace>,
  'status' | 'setStatus' | 'answer' | 'error' | 'selectedDocument'>) {
  return (<>            {status === "loading" && (
              <Card>
                <CardHeader>
                  <Skeleton className="h-5 w-32" />
                  <Skeleton className="h-4 w-64" />
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-11/12" />
                  <Skeleton className="h-4 w-3/4" />
                </CardContent>
              </Card>
            )}
            {status === "empty" && (
              <Card className="border-dashed shadow-none">
                <CardContent className="flex flex-col items-center justify-center px-6 py-16 text-center">
                  <span className="mb-4 flex size-10 items-center justify-center rounded-full bg-muted">
                    <FolderOpen className="size-4 text-muted-foreground" />
                  </span>
                  <p className="text-sm font-medium">
                    Your answer will appear here
                  </p>
                  <p className="mt-1 max-w-xs text-sm text-muted-foreground">
                    Ask a question above to search across the selected document.
                  </p>
                </CardContent>
              </Card>
            )}
            {status === "error" && (
              <Alert variant="destructive">
                <AlertCircle className="size-4" />
                <AlertTitle>Request failed</AlertTitle>
                <AlertDescription className="flex items-center justify-between gap-3">
                  {error}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setStatus("empty")}
                  >
                    Try again
                  </Button>
                </AlertDescription>
              </Alert>
            )}
            {status === "insufficient" && (
              <Alert>
                <AlertCircle className="size-4" />
                <AlertTitle>Not enough evidence</AlertTitle>
                <AlertDescription>
                  I couldn&apos;t find enough relevant information in this
                  document. Try asking about a specific section or uploading
                  another source.
                </AlertDescription>
              </Alert>
            )}
            {status === "success" && answer && (
              <Card className="shadow-sm">
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <CardTitle className="text-base">Answer</CardTitle>
                      <CardDescription className="mt-1">
                        Based on {selectedDocument?.name ?? "your document"}
                      </CardDescription>
                    </div>
                    <Badge variant="secondary">
                      {answer.sources.length} sources
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="flex flex-col gap-6">
                  <p className="text-[15px] leading-7 text-foreground/90">
                    {answer.text}
                  </p>
                  <div className="flex flex-col gap-3">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-semibold">Sources</p>
                      <p className="text-xs text-muted-foreground">
                        Click to expand excerpts
                      </p>
                    </div>
                    {answer.sources.map((source) => (
                      <SourceItem key={source.id} source={source} />
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
</>);
}
