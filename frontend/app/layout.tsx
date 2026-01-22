import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'HR Architect - AI-powered HR Policy Design',
  description: 'Design comprehensive HR policies with AI assistance and human oversight',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="font-sans">{children}</body>
    </html>
  );
}
