import ValuesPageClient from './ValuesPageClient';

export function generateStaticParams() {
  return [{ companyId: 'demo' }];
}

export default function ValuesPage() {
  return <ValuesPageClient />;
}
