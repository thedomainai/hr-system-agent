import FinalPageClient from './FinalPageClient';

export function generateStaticParams() {
  return [{ companyId: 'demo' }];
}

export default function FinalPage() {
  return <FinalPageClient />;
}
