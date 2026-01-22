import GradingPageClient from './GradingPageClient';

export function generateStaticParams() {
  return [{ companyId: 'demo' }];
}

export default function GradingPage() {
  return <GradingPageClient />;
}
