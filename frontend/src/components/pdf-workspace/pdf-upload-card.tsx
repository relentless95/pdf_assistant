import { useRef, useState, type DragEvent } from 'react';
import { Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardTitle } from '@/components/ui/card';

type Props = {
  disabled: boolean;
  onUpload: (file: File) => Promise<void>;
  onError: (message: string) => void;
};

/** File selection and dropping share the same validation and upload handler. */
export function PdfUploadCard({ disabled, onUpload, onError }: Props) {
  const input = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    // Stop the browser from opening the dropped PDF instead of uploading it.
    event.preventDefault();
    setDragging(false);
    if (disabled) return;

    const files = event.dataTransfer.files;
    if (files.length !== 1) {
      onError('Drop one PDF at a time.');
      return;
    }
    void onUpload(files[0]);
  }

  return (
    <Card
      className={`border-dashed shadow-none transition-colors ${dragging && !disabled ? 'border-primary bg-primary/5' : ''}`}
      onDragOver={(event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = disabled ? 'none' : 'copy';
        if (!disabled) setDragging(true);
      }}
      onDragLeave={(event) => {
        // Moving over children inside the card should keep the highlight.
        if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
          setDragging(false);
        }
      }}
      onDrop={handleDrop}
      aria-label="PDF upload area"
      aria-disabled={disabled}
    >
      <CardContent className="flex flex-col items-center justify-center px-6 py-10 text-center sm:py-14">
        <span className="mb-4 flex size-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <Upload className="size-5" />
        </span>
        <CardTitle className="text-base">Add a PDF to your workspace</CardTitle>
        <CardDescription className="mt-2 max-w-sm">
          Drag and drop a PDF here, or choose one from your computer.
        </CardDescription>
        <Button className="mt-5" type="button" disabled={disabled}
          onClick={() => input.current?.click()}>
          <Upload className="mr-2 size-4" /> Choose PDF
        </Button>
        <input ref={input} type="file" accept=".pdf,application/pdf"
          aria-label="Choose PDF" className="sr-only" disabled={disabled}
          onChange={(event) => {
            const file = event.target.files?.[0];
            event.target.value = '';
            if (file && !disabled) void onUpload(file);
          }} />
        <p className="mt-3 text-xs text-muted-foreground">One PDF at a time, up to 10 MiB</p>
      </CardContent>
    </Card>
  );
}
