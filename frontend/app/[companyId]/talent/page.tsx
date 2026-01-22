import TalentPageClient from './TalentPageClient';

export function generateStaticParams() {
  return [{ companyId: 'demo' }];
}

export default function TalentPage() {
  return <TalentPageClient />;
}
