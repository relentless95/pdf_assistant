import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { PdfWorkspace } from './components/pdf-workspace'
import './styles.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PdfWorkspace />
  </StrictMode>,
)
