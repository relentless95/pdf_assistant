export type DocumentRecord = {
  id: string
  name: string
  pages: number
  size: string
  added: string
}

export type SourceExcerpt = {
  id: string
  page: number
  excerpt: string
}

export const initialDocuments: DocumentRecord[] = [
  { id: 'q3-report', name: 'Q3 Product Report.pdf', pages: 18, size: '2.4 MB', added: 'Today' },
  { id: 'research', name: 'User Research Synthesis.pdf', pages: 32, size: '4.8 MB', added: 'Yesterday' },
  { id: 'handbook', name: 'Engineering Handbook.pdf', pages: 74, size: '8.1 MB', added: 'Oct 12' },
]

export const mockAnswer = {
  text: 'The product team increased activation by 18% in Q3, primarily through a shorter onboarding flow and clearer first-run guidance. The report also notes that the new checklist helped users reach their first successful workflow sooner.',
  sources: [
    { id: 'source-1', page: 6, excerpt: 'Activation increased 18% quarter over quarter after the onboarding flow was reduced from seven steps to four.' },
    { id: 'source-2', page: 8, excerpt: 'The first-run checklist was associated with a 24% faster time to first successful workflow.' },
    { id: 'source-3', page: 14, excerpt: 'Teams that completed the guided setup retained at a higher rate through the end of the quarter.' },
  ] satisfies SourceExcerpt[],
}

export const mockPdfOperations = {
  async askQuestion(question: string, documentId: string) {
    await new Promise((resolve) => setTimeout(resolve, 900))
    if (!question.trim()) throw new Error('Please enter a question to continue.')
    if (!documentId) return { status: 'insufficient' as const }
    return { status: 'success' as const, ...mockAnswer }
  },
}
