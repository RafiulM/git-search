flowchart TD
    Home[Home Page] --> Search[Search Repositories]
    Search --> SearchAPI[Call API github search]
    SearchAPI --> GitHubOcto[Octokit Query GitHub]
    GitHubOcto --> SearchAPI
    SearchAPI --> DisplayResults[Display Results]
    DisplayResults --> RepoSelect[Select Repository]
    RepoSelect --> DetailPage[Repository Detail Page]
    DetailPage --> AnalyzeAPI[Call API github analyze]
    AnalyzeAPI --> GitHubOcto
    GitHubOcto --> AnalyzeAPI
    AnalyzeAPI --> DisplayAnalysis[Display Analysis]
    DetailPage --> AIChat[AI Powered Chat]
    AIChat --> ChatAPI[Call API ai chat]
    ChatAPI --> VercelAI[Vercel AI SDK]
    VercelAI --> ChatAPI
    ChatAPI --> AIChat
    Home --> Favorites[Favorites Page]
    Favorites --> FavAPI[Call API github favorites]
    FavAPI --> SupabaseDB[Supabase Data Store]
    SupabaseDB --> FavAPI
    FavAPI --> Favorites
    Home --> Dashboard[Dashboard Page]
    Dashboard --> StatsAPI[Call API dashboard stats]
    StatsAPI --> SupabaseDB
    SupabaseDB --> StatsAPI
    StatsAPI --> Dashboard
    Home --> Auth[User Authentication]
    Auth --> ClerkAuth[Clerk Auth Service]
    ClerkAuth --> Auth
    Auth --> Home