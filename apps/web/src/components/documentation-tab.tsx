'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { FileText } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { getRepositoryDocuments } from '@/lib/api';

interface DocumentationTabProps {
  repositoryId: string;
  owner: string;
  repo: string;
}

export function DocumentationTab({ repositoryId, owner, repo }: DocumentationTabProps) {
  const router = useRouter();
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [documentTypes, setDocumentTypes] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await getRepositoryDocuments(repositoryId, {
          current_only: true,
          summary_only: true
        });
        const docs = response?.documents || [];
        const types = Array.from(new Set(docs.map(doc => doc.document_type)));
        setDocumentTypes(types);
        
        if (types.length > 0 && !isRedirecting) {
          setIsRedirecting(true);
          const firstDocType = types[0];
          // Use setTimeout to defer the navigation to avoid hydration issues
          setTimeout(() => {
            router.push(`/repository/${owner}/${repo}/docs/${firstDocType}`);
          }, 100);
        }
      } catch (error) {
        console.error('Error fetching documents:', error);
        setDocumentTypes([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocuments();
  }, [repositoryId, owner, repo, router, isRedirecting]);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <FileText className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">Loading Documentation...</h3>
          <p className="text-muted-foreground">
            Please wait while we fetch the documentation
          </p>
        </CardContent>
      </Card>
    );
  }

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