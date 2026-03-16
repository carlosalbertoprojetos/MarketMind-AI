import ContentEditor from "@/components/ContentEditor";

export default function ContentStudioPage() {
  return (
    <div className="space-y-6">
      <header className="card p-8">
        <h1 className="section-title text-2xl font-semibold">Content Studio</h1>
        <p className="mt-2 text-sm text-gray-600">
          Central de criacao, derivacao e refinamento de conteudo multiformato.
        </p>
      </header>
      <ContentEditor />
    </div>
  );
}