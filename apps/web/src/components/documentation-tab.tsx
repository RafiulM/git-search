'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { FileText } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tables } from '@/types/database.types';

type Document = Tables<'documents'>;

interface DocumentationTabProps {
  documents: Document[];
  owner: string;
  repo: string;
}

export function DocumentationTab({ documents, owner, repo }: DocumentationTabProps) {
  const router = useRouter();
  const [isRedirecting, setIsRedirecting] = useState(false);
  const documentTypes = Array.from(new Set(documents.map(doc => doc.document_type)));

  useEffect(() => {
    if (documentTypes.length > 0 && !isRedirecting) {
      setIsRedirecting(true);
      const firstDocType = documentTypes[0];
      // Use setTimeout to defer the navigation to avoid hydration issues
      setTimeout(() => {
        router.push(`/repository/${owner}/${repo}/docs/${firstDocType}`);
      }, 100);
    }
  }, [documentTypes, owner, repo, router, isRedirecting]);

  if (documentTypes.length > 0) {
    const firstDocType = documentTypes[0];
    return (
      <Card>
        <CardContent className="text-center py-12">
          <FileText className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">Redirecting to Documentation...</h3>
          <p className="text-muted-foreground">
            Taking you to {firstDocType} documentation
          </p>
        </CardContent>
      </Card>
    );
  } else {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <FileText className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">No Documentation Available</h3>
          <p className="text-muted-foreground mb-6">
            Generate comprehensive documentation for this repository.
          </p>
          <div className="flex justify-center">
            <Button>
              Generate Documentation
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }
}