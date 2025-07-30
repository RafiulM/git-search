import { NextRequest, NextResponse } from 'next/server';
import { Octokit } from '@octokit/rest';
import { createSupabaseServerClient } from '@/lib/supabase';

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN,
});

function estimateTokens(text: string, model: string): number {
  const charCount = text.length;
  
  switch (model) {
    case 'gpt4':
      return Math.ceil(charCount / 3.5);
    case 'claude3':
      return Math.ceil(charCount / 4.5);
    case 'gemini':
      return Math.ceil(charCount / 4);
    default:
      return Math.ceil(charCount / 4);
  }
}

function calculateComplexityScore(files: { name: string; size?: number }[]): number {
  let totalComplexity = 0;
  
  files.forEach(file => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    let baseComplexity = 1;
    
    switch (extension) {
      case 'js':
      case 'ts':
      case 'jsx':
      case 'tsx':
        baseComplexity = 3;
        break;
      case 'py':
      case 'java':
      case 'cpp':
      case 'c':
        baseComplexity = 4;
        break;
      case 'html':
      case 'css':
      case 'md':
        baseComplexity = 1;
        break;
      case 'json':
      case 'yaml':
      case 'yml':
        baseComplexity = 0.5;
        break;
      default:
        baseComplexity = 2;
    }
    
    totalComplexity += baseComplexity * (file.size || 0) / 1000;
  });
  
  return Math.min(Math.round(totalComplexity / files.length * 10) / 10, 10);
}

async function analyzeRepository(owner: string, repo: string) {
  try {
    const { data: contents } = await octokit.rest.repos.getContent({
      owner,
      repo,
      path: '',
    });

    const files: { path: string; name: string; extension: string; size: number; type: string }[] = [];
    const languages: Record<string, number> = {};
    const fileTypes: Record<string, number> = {};
    let totalLines = 0;
    let totalChars = 0;
    let totalSize = 0;

    async function analyzeContents(items: { name: string; path: string; type: string; size?: number }[], path = '') {
      for (const item of items) {
        if (item.type === 'file') {
          const extension = item.name.split('.').pop()?.toLowerCase() || 'unknown';
          const size = item.size || 0;
          
          files.push({
            path: path ? `${path}/${item.name}` : item.name,
            name: item.name,
            extension,
            size,
            type: item.type,
          });

          fileTypes[extension] = (fileTypes[extension] || 0) + 1;
          totalSize += size;

          if (size < 100000 && !item.name.match(/\.(jpg|jpeg|png|gif|pdf|zip|tar|gz)$/i)) {
            try {
              const { data: fileContent } = await octokit.rest.repos.getContent({
                owner,
                repo,
                path: item.path,
              });

              if ('content' in fileContent && fileContent.content) {
                const content = Buffer.from(fileContent.content, 'base64').toString('utf-8');
                const lines = content.split('\n').length;
                const chars = content.length;
                
                totalLines += lines;
                totalChars += chars;

                const language = getLanguageFromExtension(extension);
                if (language) {
                  languages[language] = (languages[language] || 0) + lines;
                }
              }
            } catch (error) {
              console.warn(`Could not analyze file ${item.path}:`, error);
            }
          }
        } else if (item.type === 'dir' && path.split('/').length < 3) {
          try {
            const { data: dirContents } = await octokit.rest.repos.getContent({
              owner,
              repo,
              path: item.path,
            });
            
            if (Array.isArray(dirContents)) {
              await analyzeContents(dirContents, item.path);
            }
          } catch (error) {
            console.warn(`Could not analyze directory ${item.path}:`, error);
          }
        }
      }
    }

    if (Array.isArray(contents)) {
      await analyzeContents(contents);
    }

    const complexityScore = calculateComplexityScore(files);
    const maintainabilityIndex = Math.max(0, 100 - complexityScore * 10);

    const statistics = {
      total_lines: totalLines,
      total_characters: totalChars,
      file_count: files.length,
      directory_count: files.filter(f => f.type === 'dir').length,
      estimated_tokens_gpt4: estimateTokens(totalChars.toString(), 'gpt4'),
      estimated_tokens_claude3: estimateTokens(totalChars.toString(), 'claude3'),
      estimated_tokens_gemini: estimateTokens(totalChars.toString(), 'gemini'),
      storage_size_bytes: totalSize,
      language_breakdown: languages,
      file_type_breakdown: fileTypes,
      largest_files: files
        .sort((a, b) => (b.size || 0) - (a.size || 0))
        .slice(0, 10)
        .map(f => ({ path: f.path, size: f.size })),
      complexity_score: complexityScore,
      maintainability_index: maintainabilityIndex,
    };

    return { statistics, files };
  } catch (error) {
    console.error('Repository analysis error:', error);
    throw error;
  }
}

function getLanguageFromExtension(ext: string): string | null {
  const langMap: Record<string, string> = {
    'js': 'JavaScript',
    'jsx': 'JavaScript',
    'ts': 'TypeScript',
    'tsx': 'TypeScript',
    'py': 'Python',
    'java': 'Java',
    'cpp': 'C++',
    'c': 'C',
    'cs': 'C#',
    'php': 'PHP',
    'rb': 'Ruby',
    'go': 'Go',
    'rs': 'Rust',
    'swift': 'Swift',
    'kt': 'Kotlin',
    'scala': 'Scala',
    'html': 'HTML',
    'css': 'CSS',
    'scss': 'SCSS',
    'sass': 'Sass',
    'vue': 'Vue',
    'svelte': 'Svelte',
    'md': 'Markdown',
    'sql': 'SQL',
    'sh': 'Shell',
    'yml': 'YAML',
    'yaml': 'YAML',
    'json': 'JSON',
    'xml': 'XML',
    'dockerfile': 'Docker',
  };
  
  return langMap[ext] || null;
}

export async function POST(request: NextRequest) {
  try {
    const { owner, repo } = await request.json();

    if (!owner || !repo) {
      return NextResponse.json(
        { error: 'Owner and repository name are required' },
        { status: 400 }
      );
    }

    const supabase = await createSupabaseServerClient();

    const { data: githubRepo } = await octokit.rest.repos.get({
      owner,
      repo,
    });

    let existingRepo;
    const { data: repoData } = await supabase
      .from('repositories')
      .select('*')
      .eq('github_id', githubRepo.id)
      .single();

    if (repoData) {
      existingRepo = repoData;
    } else {
      const { data: newRepo } = await supabase
        .from('repositories')
        .insert({
          github_id: githubRepo.id,
          full_name: githubRepo.full_name,
          name: githubRepo.name,
          owner_login: githubRepo.owner.login,
          description: githubRepo.description,
          html_url: githubRepo.html_url,
          clone_url: githubRepo.clone_url,
          ssh_url: githubRepo.ssh_url,
          default_branch: githubRepo.default_branch,
          language: githubRepo.language,
          topics: githubRepo.topics || [],
          stars_count: githubRepo.stargazers_count,
          forks_count: githubRepo.forks_count,
          watchers_count: githubRepo.watchers_count,
          open_issues_count: githubRepo.open_issues_count,
          size_kb: githubRepo.size,
          github_created_at: githubRepo.created_at,
          github_updated_at: githubRepo.updated_at,
          is_private: githubRepo.private,
          is_fork: githubRepo.fork,
          is_archived: githubRepo.archived,
          license_name: githubRepo.license?.name,
          has_wiki: githubRepo.has_wiki,
          has_pages: githubRepo.has_pages,
          has_downloads: githubRepo.has_downloads,
          has_issues: githubRepo.has_issues,
          has_projects: githubRepo.has_projects,
        })
        .select()
        .single();
      
      existingRepo = newRepo;
    }

    const { data: analysisJob } = await supabase
      .from('analysis_jobs')
      .insert({
        repository_id: existingRepo.id,
        job_type: 'full_analysis',
        status: 'running',
      })
      .select()
      .single();

    try {
      const { statistics, files } = await analyzeRepository(owner, repo);

      await supabase
        .from('repository_statistics')
        .upsert({
          repository_id: existingRepo.id,
          ...statistics,
        });

      await supabase
        .from('repository_files')
        .delete()
        .eq('repository_id', existingRepo.id);

      if (files.length > 0) {
        await supabase
          .from('repository_files')
          .insert(
            files.map(file => ({
              repository_id: existingRepo.id,
              file_path: file.path,
              file_name: file.name,
              file_extension: file.extension,
              file_size_bytes: file.size || 0,
              language: getLanguageFromExtension(file.extension),
              is_binary: file.name.match(/\.(jpg|jpeg|png|gif|pdf|zip|tar|gz|exe|dll|so)$/i) !== null,
            }))
          );
      }

      await supabase
        .from('repositories')
        .update({ last_analyzed_at: new Date().toISOString() })
        .eq('id', existingRepo.id);

      await supabase
        .from('analysis_jobs')
        .update({
          status: 'completed',
          progress: 100,
          completed_at: new Date().toISOString(),
        })
        .eq('id', analysisJob.id);

      return NextResponse.json({
        success: true,
        repository: existingRepo,
        statistics,
        message: 'Repository analyzed successfully',
      });

    } catch (analysisError) {
      await supabase
        .from('analysis_jobs')
        .update({
          status: 'failed',
          error_message: (analysisError as Error).message,
          completed_at: new Date().toISOString(),
        })
        .eq('id', analysisJob.id);

      throw analysisError;
    }

  } catch (error) {
    console.error('Analysis API error:', error);
    return NextResponse.json(
      { error: 'Failed to analyze repository' },
      { status: 500 }
    );
  }
}