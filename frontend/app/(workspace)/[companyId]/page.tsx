import WorkspacePageClient from './WorkspacePageClient';

export function generateStaticParams() {
  return [{ companyId: 'demo' }];
}

interface PageProps {
  params: Promise<{ companyId: string }>;
}

export default function WorkspacePage({ params }: PageProps) {
  return <WorkspacePageClient params={params} />;
}
