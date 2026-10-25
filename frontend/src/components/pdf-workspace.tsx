'use client'

import { useMemo, useState } from 'react'
import { AlertCircle, CheckCircle2, FileText, FolderOpen, Loader2, MoreHorizontal, Plus, Send, Sparkles, Trash2, Upload, X } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { Textarea } from '@/components/ui/textarea'
import { initialDocuments, mockPdfOperations, type DocumentRecord, type SourceExcerpt } from '@/lib/mock-pdf-operations'

function DocumentList({ documents, selectedId, onSelect, onDelete }: { documents: DocumentRecord[]; selectedId: string; onSelect: (id: string) => void; onDelete: (id: string) => void }) {
  return (
    <div className="flex flex-col gap-2">
      {documents.map((document) => (
        <div key={document.id} className={`group flex items-center gap-3 rounded-lg border px-3 py-3 transition-colors ${selectedId === document.id ? 'border-primary/20 bg-primary/[0.06]' : 'border-transparent hover:border-border hover:bg-muted/60'}`}>
          <button onClick={() => onSelect(document.id)} className="flex min-w-0 flex-1 items-center gap-3 text-left" aria-pressed={selectedId === document.id}>
            <span className="flex size-9 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground"><FileText className="size-4" /></span>
            <span className="min-w-0"><span className="block truncate text-sm font-medium">{document.name}</span><span className="mt-1 block text-xs text-muted-foreground">{document.pages} pages · {document.size}</span></span>
          </button>
          <Button variant="ghost" size="icon" className="size-8 shrink-0 text-muted-foreground opacity-60 hover:text-destructive group-hover:opacity-100" onClick={() => onDelete(document.id)} aria-label={`Delete ${document.name}`}><Trash2 className="size-4" /></Button>
        </div>
      ))}
    </div>
  )
}

function SourceItem({ source }: { source: SourceExcerpt }) {
  const [open, setOpen] = useState(false)
  return <button className="w-full rounded-lg border bg-background p-3 text-left transition-colors hover:bg-muted/40" onClick={() => setOpen(!open)} aria-expanded={open}>
    <span className="flex items-center justify-between gap-4"><span className="flex items-center gap-2 text-sm font-medium"><span className="flex size-6 items-center justify-center rounded bg-muted text-xs text-muted-foreground">{source.page}</span>Page {source.page}</span><span className="text-xs text-muted-foreground">{open ? 'Hide excerpt' : 'View excerpt'}</span></span>
    {open && <span className="mt-3 block border-t pt-3 text-sm leading-6 text-muted-foreground">“{source.excerpt}”</span>}
  </button>
}

export function PdfWorkspace() {
  const [documents, setDocuments] = useState(initialDocuments)
  const [selectedId, setSelectedId] = useState(initialDocuments[0]?.id ?? '')
  const [question, setQuestion] = useState('')
  const [status, setStatus] = useState<'empty' | 'loading' | 'success' | 'error' | 'insufficient'>('empty')
  const [answer, setAnswer] = useState<{ text: string; sources: SourceExcerpt[] } | null>(null)
  const [error, setError] = useState('')
  const selectedDocument = useMemo(() => documents.find((document) => document.id === selectedId), [documents, selectedId])

  async function handleAsk() {
    setStatus('loading'); setError('')
    try {
      const result = await mockPdfOperations.askQuestion(question, selectedId)
      if (result.status === 'insufficient') { setStatus('insufficient'); setAnswer(null); return }
      setAnswer({ text: result.text, sources: result.sources }); setStatus('success')
    } catch (caught) { setError(caught instanceof Error ? caught.message : 'Something went wrong.'); setStatus('error') }
  }

  function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return
    const newDocument = { id: `${file.name}-${Date.now()}`, name: file.name, pages: 1, size: `${(file.size / 1024 / 1024).toFixed(1)} MB`, added: 'Just now' }
    setDocuments((current) => [newDocument, ...current]); setSelectedId(newDocument.id)
  }

  function deleteDocument(id: string) {
    const next = documents.filter((document) => document.id !== id); setDocuments(next)
    if (selectedId === id) setSelectedId(next[0]?.id ?? '')
  }

  return <main className="min-h-screen bg-muted/30 text-foreground"><div className="mx-auto flex min-h-screen max-w-[1440px] flex-col lg:flex-row">
    <aside className="flex w-full shrink-0 flex-col border-b bg-background lg:w-[292px] lg:border-b-0 lg:border-r"><div className="flex items-center justify-between px-5 py-5"><div className="flex items-center gap-2.5"><span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground"><Sparkles className="size-4" /></span><span className="font-semibold tracking-tight">Atlas<span className="text-muted-foreground">/</span>pdf</span></div><Button variant="ghost" size="icon" className="size-8"><MoreHorizontal className="size-4" /></Button></div><Separator /><div className="flex flex-1 flex-col gap-5 p-4"><div className="flex items-center justify-between"><div><p className="text-sm font-semibold">Your documents</p><p className="mt-1 text-xs text-muted-foreground">{documents.length} files in workspace</p></div><label htmlFor="sidebar-upload"><Button variant="outline" size="icon" className="size-8" aria-label="Upload PDF" onClick={() => document.getElementById("sidebar-upload")?.click()}><Plus className="size-4" /></Button><input id="sidebar-upload" type="file" accept="application/pdf" className="sr-only" onChange={handleUpload} /></label></div><ScrollArea className="max-h-[300px] lg:max-h-none"><DocumentList documents={documents} selectedId={selectedId} onSelect={setSelectedId} onDelete={deleteDocument} /></ScrollArea><div className="mt-auto hidden rounded-lg border bg-muted/40 p-3 lg:block"><div className="flex items-center gap-2 text-xs font-medium"><CheckCircle2 className="size-4 text-primary" /> Local demo mode</div><p className="mt-2 text-xs leading-5 text-muted-foreground">Mock operations are ready to replace with your FastAPI client.</p></div></div></aside>
    <section className="flex min-w-0 flex-1 flex-col"><header className="flex items-center justify-between border-b bg-background px-5 py-4 sm:px-8"><div><p className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">Document workspace</p><h1 className="mt-1 text-lg font-semibold tracking-tight">Ask your PDFs</h1></div><Badge variant="secondary" className="gap-1.5 font-normal"><span className="size-1.5 rounded-full bg-emerald-500" /> Ready</Badge></header><div className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-6 p-5 sm:p-8 lg:p-12"><Card className="border-dashed shadow-none"><CardContent className="flex flex-col items-center justify-center px-6 py-10 text-center sm:py-14"><span className="mb-4 flex size-12 items-center justify-center rounded-xl bg-primary/10 text-primary"><Upload className="size-5" /></span><CardTitle className="text-base">Add a PDF to your workspace</CardTitle><CardDescription className="mt-2 max-w-sm">Upload a document and ask questions grounded in its content.</CardDescription><label htmlFor="main-upload" className="mt-5"><Button type="button" onClick={() => document.getElementById("main-upload")?.click()}><Upload className="mr-2 size-4" /> Choose PDF</Button><input id="main-upload" type="file" accept="application/pdf" className="sr-only" onChange={handleUpload} /></label><p className="mt-3 text-xs text-muted-foreground">PDF files up to 10 MiB</p></CardContent></Card>
      <Card className="shadow-sm"><CardHeader className="pb-4"><div className="flex items-start justify-between gap-4"><div><CardTitle className="text-base">Ask a question</CardTitle><CardDescription className="mt-1">Get a concise answer with traceable sources.</CardDescription></div>{selectedDocument && <Badge variant="outline" className="hidden max-w-[220px] truncate sm:flex"><FileText className="mr-1.5 size-3" />{selectedDocument.name}</Badge>}</div></CardHeader><CardContent><div className="flex flex-col gap-3 sm:flex-row sm:items-end"><Textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What would you like to know about this document?" className="min-h-[88px] resize-none bg-muted/30 sm:min-h-[52px]" onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing && event.keyCode !== 229) { event.preventDefault(); void handleAsk() } }} /><Button onClick={() => void handleAsk()} disabled={status === 'loading'} className="h-11 shrink-0 sm:h-[52px]">{status === 'loading' ? <Loader2 className="mr-2 size-4 animate-spin" /> : <Send className="mr-2 size-4" />} Ask question</Button></div><p className="mt-3 text-xs text-muted-foreground">Press Enter to ask · Shift + Enter for a new line</p></CardContent></Card>
      {status === 'loading' && <Card><CardHeader><Skeleton className="h-5 w-32" /><Skeleton className="h-4 w-64" /></CardHeader><CardContent className="flex flex-col gap-3"><Skeleton className="h-4 w-full" /><Skeleton className="h-4 w-11/12" /><Skeleton className="h-4 w-3/4" /></CardContent></Card>}
      {status === 'empty' && <Card className="border-dashed shadow-none"><CardContent className="flex flex-col items-center justify-center px-6 py-16 text-center"><span className="mb-4 flex size-10 items-center justify-center rounded-full bg-muted"><FolderOpen className="size-4 text-muted-foreground" /></span><p className="text-sm font-medium">Your answer will appear here</p><p className="mt-1 max-w-xs text-sm text-muted-foreground">Ask a question above to search across the selected document.</p></CardContent></Card>}
      {status === 'error' && <Alert variant="destructive"><AlertCircle className="size-4" /><AlertTitle>We couldn&apos;t answer that</AlertTitle><AlertDescription className="flex items-center justify-between gap-3">{error}<Button variant="outline" size="sm" onClick={() => setStatus('empty')}>Try again</Button></AlertDescription></Alert>}
      {status === 'insufficient' && <Alert><AlertCircle className="size-4" /><AlertTitle>Not enough evidence</AlertTitle><AlertDescription>I couldn&apos;t find enough relevant information in this document. Try asking about a specific section or uploading another source.</AlertDescription></Alert>}
      {status === 'success' && answer && <Card className="shadow-sm"><CardHeader><div className="flex items-center justify-between gap-3"><div><CardTitle className="text-base">Answer</CardTitle><CardDescription className="mt-1">Based on {selectedDocument?.name ?? 'your document'}</CardDescription></div><Badge variant="secondary">3 sources</Badge></div></CardHeader><CardContent className="flex flex-col gap-6"><p className="text-[15px] leading-7 text-foreground/90">{answer.text}</p><div className="flex flex-col gap-3"><div className="flex items-center justify-between"><p className="text-sm font-semibold">Sources</p><p className="text-xs text-muted-foreground">Click to expand excerpts</p></div>{answer.sources.map((source) => <SourceItem key={source.id} source={source} />)}</div></CardContent></Card>}
    </div></section>
  </div></main>
}
