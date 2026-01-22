import CompensationPageClient from './CompensationPageClient';

export function generateStaticParams() {
  return [{ companyId: 'demo' }];
}

export default function CompensationPage() {
  return <CompensationPageClient />;
}
