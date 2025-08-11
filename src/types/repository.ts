export interface Repository {
  id: string
  name: string
  description: string | null
  language: string | null
  stars: number
  forks: number
  isPrivate: boolean
  lastUpdated: string
  owner: {
    name: string
    avatar: string
  }
  url: string
}

export interface RepositoryOwner {
  name: string
  avatar: string
}

// Language color mapping for display purposes
export const LANGUAGE_COLORS: Record<string, string> = {
  TypeScript: '#3178c6',
  JavaScript: '#f1e05a',
  Python: '#3572A5',
  Go: '#00ADD8',
  Rust: '#dea584',
  Java: '#b07219',
  'C++': '#f34b7d',
  C: '#555555',
  HTML: '#e34c26',
  CSS: '#563d7c',
  Vue: '#4FC08D',
  React: '#61dafb',
  Svelte: '#ff3e00',
  PHP: '#4F5D95',
  Ruby: '#701516',
  Swift: '#fa7343',
  Kotlin: '#A97BFF',
  Dart: '#00B4AB',
  Shell: '#89e051',
  Dockerfile: '#384d54',
}