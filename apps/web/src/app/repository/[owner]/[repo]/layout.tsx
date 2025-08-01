import { ReactNode } from 'react';

interface RepositoryLayoutProps {
  children: ReactNode;
}

export default function RepositoryLayout({
  children,
}: RepositoryLayoutProps) {
  return <>{children}</>;
}