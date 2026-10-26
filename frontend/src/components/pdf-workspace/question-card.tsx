import { FileText, Loader2, Send } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { usePdfWorkspace } from '@/hooks/use-pdf-workspace';

export function QuestionCard({ question, setQuestion, selectedId, selectedDocument,
  busy, status, handleAsk }: Pick<ReturnType<typeof usePdfWorkspace>,
  'question' | 'setQuestion' | 'selectedId' | 'selectedDocument' | 'busy' | 'status' | 'handleAsk'>) {
  return (<Card className="shadow-sm">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <CardTitle className="text-base">Ask a question</CardTitle>
                    <CardDescription className="mt-1">
                      Get a concise answer with traceable sources.
                    </CardDescription>
                  </div>
                  {selectedDocument && (
                    <Badge
                      variant="outline"
                      className="hidden max-w-[220px] truncate sm:flex"
                    >
                      <FileText className="mr-1.5 size-3" />
                      {selectedDocument.name}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                  <Textarea
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="What would you like to know about this document?"
                    className="min-h-[88px] resize-none bg-muted/30 sm:min-h-[52px]"
                    disabled={busy}
                    maxLength={2000}
                    onKeyDown={(event) => {
                      if (
                        event.key === "Enter" &&
                        !event.shiftKey &&
                        !event.nativeEvent.isComposing &&
                        event.keyCode !== 229
                      ) {
                        event.preventDefault();
                        void handleAsk();
                      }
                    }}
                  />
                  <Button
                    onClick={() => void handleAsk()}
                    disabled={busy || !selectedId || !question.trim()}
                    className="h-11 shrink-0 sm:h-[52px]"
                  >
        {status === "loading" ? (
                      <Loader2 className="mr-2 size-4 animate-spin" />
                    ) : (
                      <Send className="mr-2 size-4" />
                    )}{" "}
                    Ask question
                  </Button>
                </div>
                <p className="mt-3 text-xs text-muted-foreground">
                  Press Enter to ask · Shift + Enter for a new line
                </p>
              </CardContent>
            </Card>
            );
}
