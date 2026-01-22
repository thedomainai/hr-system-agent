import EvaluationPageClient from './EvaluationPageClient';

export function generateStaticParams() {
  return [{ companyId: 'demo' }];
}

export default function EvaluationPage() {
  return <EvaluationPageClient />;
}
