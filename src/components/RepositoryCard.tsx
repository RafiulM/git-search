'use client'

import { Repository, LANGUAGE_COLORS } from '@/types/repository'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Star, GitFork, Clock, Lock } from 'lucide-react'
import { cn } from '@/lib/utils'

interface RepositoryCardProps {
  repository: Repository
  className?: string
}

export function RepositoryCard({ repository, className }: RepositoryCardProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'Updated now'
    if (diffInHours < 24) return `Updated ${diffInHours}h ago`
    if (diffInHours < 168) return `Updated ${Math.floor(diffInHours / 24)}d ago`
    return `Updated ${Math.floor(diffInHours / 168)}w ago`
  }

  const getLanguageColor = (language: string | null) => {
    if (!language) return '#6b7280'
    return LANGUAGE_COLORS[language] || '#6b7280'
  }

  return (
    <Card 
      className={cn(
        'group cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-[1.02] h-full',
        className
      )}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="flex items-center gap-2 text-lg group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
              {repository.isPrivate && (
                <Lock className="h-4 w-4 text-muted-foreground" />
              )}
              <span className="truncate">{repository.name}</span>
            </CardTitle>
            <CardDescription className="mt-2 line-clamp-2">
              {repository.description || 'No description available'}
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4" />
            <span>{repository.stars.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <GitFork className="h-4 w-4" />
            <span>{repository.forks.toLocaleString()}</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          {repository.language && (
            <Badge 
              variant="outline" 
              className="flex items-center gap-1"
            >
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: getLanguageColor(repository.language) }}
              />
              {repository.language}
            </Badge>
          )}
        </div>
      </CardContent>

      <CardFooter className="pt-0">
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <Clock className="h-3 w-3" />
          <span>{formatDate(repository.lastUpdated)}</span>
        </div>
      </CardFooter>
    </Card>
  )
}