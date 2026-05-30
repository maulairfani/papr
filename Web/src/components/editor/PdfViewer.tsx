/** Renders a PDF in the browser's built-in viewer. `src` is a URL — later a blob
 * URL built from the store's base64 PDF. */
export function PdfViewer({ src }: { src?: string }) {
  if (!src) {
    return <div className="grid h-full place-items-center text-sm text-muted">No PDF selected</div>;
  }
  return <iframe src={src} title="PDF" className="h-full w-full border-0" />;
}
