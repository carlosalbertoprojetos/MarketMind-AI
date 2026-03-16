import CampaignBoard from "@/components/CampaignBoard";

export default function CampaignsPage() {
  return (
    <div className="space-y-6">
      <header className="card p-8">
        <h1 className="section-title text-2xl font-semibold">Campaign Manager</h1>
        <p className="mt-2 text-sm text-gray-600">
          Orquestre campanhas por estagio: awareness, education, solution, proof e conversion.
        </p>
      </header>
      <CampaignBoard />
    </div>
  );
}