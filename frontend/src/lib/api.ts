export type DocumentRecord = {
  id: string
  name: string
  pages?: number
  size?: string
}

export type SourceExcerpt = {
  id: string
  page: number
  excerpt: string
}

type DocumentListResponse = {
  documents: {
    document_id: string
    filename: string
  }[]
}

type UploadResponse = {
  document_id: string
  filename: string
  page_count: number
}

type AnswerResponse = {
  document_id: string
  question: string
  answer: string
  insufficient_evidence: boolean
  sources: {
    chunk_id: string
    page_number: number
    content: string
  }[]
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`/api${path}`, options)

  if (!response.ok) {
    const body = await response.json().catch(() => null)

    const message =
      typeof body?.detail === 'string'
        ? body.detail
        : `Request failed (${response.status})`

    throw new Error(message)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

export function checkHealth(): Promise<{ status: string }> {
  return request('/health')
}

export async function listDocuments(): Promise<DocumentRecord[]> {
  const data = await request<DocumentListResponse>('/documents/')

  return data.documents.map((document) => ({
    id: document.document_id,
    name: document.filename,
  }))
}

export async function uploadPdf(file: File): Promise<DocumentRecord> {
  const form = new FormData()
  form.append('file', file)

  const data = await request<UploadResponse>('/files/', {
    method: 'POST',
    body: form,
  })

  return {
    id: data.document_id,
    name: data.filename,
    pages: data.page_count,
    size: `${(file.size / 1024 / 1024).toFixed(1)} MiB`,
  }
}

export async function askQuestion(
  documentId: string,
  question: string,
) {
  const data = await request<AnswerResponse>(
    `/documents/${encodeURIComponent(documentId)}/ask`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    },
  )

  return {
    text: data.answer,
    insufficientEvidence: data.insufficient_evidence,
    sources: data.sources.map((source) => ({
      id: source.chunk_id,
      page: source.page_number,
      excerpt: source.content,
    })),
  }
}

export async function deleteSavedDocument(
  documentId: string,
): Promise<void> {
  await request<void>(
    `/documents/${encodeURIComponent(documentId)}`,
    { method: 'DELETE' },
  )
}