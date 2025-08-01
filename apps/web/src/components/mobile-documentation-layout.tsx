import { FileText, Code, Database, Settings, Activity, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';
import { Tables } from '@/types/database.types';

type Document = Tables<'documents'>;

interface MobileDocumentationLayoutProps {
  owner: string;
  repo: string;
  currentDocType: string;
  documents: Document[];
  children: React.ReactNode;
}

export function MobileDocumentationLayout({
  owner,
  repo,
  currentDocType,
  documents,
  children,
}: MobileDocumentationLayoutProps) {
  const allDocumentTypes = Array.from(new Set(documents.map(doc => doc.document_type)));

  const getIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'README': return <FileText className="w-4 h-4" />;
      case 'API': return <Code className="w-4 h-4" />;
      case 'ARCHITECTURE': return <Database className="w-4 h-4" />;
      case 'SETUP': return <Settings className="w-4 h-4" />;
      case 'CONTRIBUTING': return <Activity className="w-4 h-4" />;
      case 'CHANGELOG': return <Calendar className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <div className="w-full">
      {/* Mobile Navigation - Always Visible */}
      <div className="lg:hidden mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Documentation</CardTitle>
            <CardDescription className="text-sm">Navigate between document types</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-2">
              {allDocumentTypes.map((docType) => {
                const docTitle = documents.find(doc => doc.document_type === docType)?.title || docType;
                return (
                  <Link 
                    key={docType} 
                    href={`/repository/${owner}/${repo}/docs/${docType}`}
                    className="w-full"
                  >
                    <Button 
                      variant={docType === currentDocType ? "default" : "outline"} 
                      size="sm"
                      className="w-full flex items-center gap-2 justify-start"
                    >
                      {getIcon(docType)}
                      <span>{docTitle}</span>
                    </Button>
                  </Link>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Desktop Layout */}
      <div className="hidden lg:flex gap-8">
        {/* Desktop Sidebar */}
        <div className="w-64 flex-shrink-0">
          <Card className="sticky top-4">
            <CardHeader>
              <CardTitle className="text-lg">Documentation</CardTitle>
              <CardDescription>Navigate between document types</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {allDocumentTypes.map((docType) => (
                <Link 
                  key={docType} 
                  href={`/repository/${owner}/${repo}/docs/${docType}`}
                >
                  <Button 
                    variant={docType === currentDocType ? "default" : "ghost"} 
                    className="w-full justify-start"
                  >
                    {getIcon(docType)}
                    <span className="ml-2">{docType}</span>
                  </Button>
                </Link>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Desktop Content */}
        <div className="flex-1">
          {children}
        </div>
      </div>

      {/* Mobile Content */}
      <div className="lg:hidden">
        {children}
      </div>
    </div>
  );
}