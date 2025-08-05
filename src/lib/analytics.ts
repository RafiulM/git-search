interface SearchEvent {
  id: string;
  query: string;
  filters: Record<string, any>;
  results_count: number;
  response_time_ms: number;
  cached: boolean;
  client_id: string;
  timestamp: number;
  error?: string;
  rate_limited?: boolean;
}

interface SearchStats {
  totalSearches: number;
  uniqueQueries: number;
  averageResponseTime: number;
  cacheHitRate: number;
  errorRate: number;
  rateLimitRate: number;
  topQueries: Array<{ query: string; count: number }>;
  topFilters: Array<{ filter: string; value: string; count: number }>;
  searchTrends: Array<{ hour: number; count: number }>;
  responseTimePercentiles: {
    p50: number;
    p90: number;
    p95: number;
    p99: number;
  };
}

class SearchAnalytics {
  private events: SearchEvent[] = [];
  private readonly maxEvents = 10000; // Keep last 10k events in memory
  private cleanupInterval: NodeJS.Timeout;

  constructor() {
    // Clean up old events every hour
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 60 * 60 * 1000);
  }

  trackSearch(event: Omit<SearchEvent, 'id' | 'timestamp'>): void {
    const searchEvent: SearchEvent = {
      ...event,
      id: this.generateId(),
      timestamp: Date.now(),
    };

    this.events.push(searchEvent);

    // Keep only the most recent events
    if (this.events.length > this.maxEvents) {
      this.events = this.events.slice(-this.maxEvents);
    }

    console.log(`Analytics: Search tracked - Query: "${event.query}", Results: ${event.results_count}, Time: ${event.response_time_ms}ms`);
  }

  trackError(query: string, filters: Record<string, any>, error: string, client_id: string): void {
    this.trackSearch({
      query,
      filters,
      results_count: 0,
      response_time_ms: 0,
      cached: false,
      client_id,
      error,
    });
  }

  trackRateLimit(query: string, filters: Record<string, any>, client_id: string): void {
    this.trackSearch({
      query,
      filters,
      results_count: 0,
      response_time_ms: 0,
      cached: false,
      client_id,
      rate_limited: true,
    });
  }

  getStats(timeRangeMs?: number): SearchStats {
    const now = Date.now();
    const cutoff = timeRangeMs ? now - timeRangeMs : 0;
    const relevantEvents = this.events.filter(event => event.timestamp >= cutoff);

    if (relevantEvents.length === 0) {
      return this.getEmptyStats();
    }

    const totalSearches = relevantEvents.length;
    const uniqueQueries = new Set(relevantEvents.map(e => e.query.toLowerCase().trim())).size;
    
    const responseTimes = relevantEvents.filter(e => e.response_time_ms > 0).map(e => e.response_time_ms);
    const averageResponseTime = responseTimes.length > 0 
      ? responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length 
      : 0;

    const cachedEvents = relevantEvents.filter(e => e.cached);
    const cacheHitRate = totalSearches > 0 ? (cachedEvents.length / totalSearches) * 100 : 0;

    const errorEvents = relevantEvents.filter(e => e.error);
    const errorRate = totalSearches > 0 ? (errorEvents.length / totalSearches) * 100 : 0;

    const rateLimitEvents = relevantEvents.filter(e => e.rate_limited);
    const rateLimitRate = totalSearches > 0 ? (rateLimitEvents.length / totalSearches) * 100 : 0;

    // Top queries
    const queryCount = new Map<string, number>();
    relevantEvents.forEach(event => {
      const normalizedQuery = event.query.toLowerCase().trim();
      queryCount.set(normalizedQuery, (queryCount.get(normalizedQuery) || 0) + 1);
    });
    const topQueries = Array.from(queryCount.entries())
      .map(([query, count]) => ({ query, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // Top filters
    const filterCount = new Map<string, number>();
    relevantEvents.forEach(event => {
      Object.entries(event.filters).forEach(([key, value]) => {
        if (value && key !== 'sort' && key !== 'order') {
          const filterKey = `${key}:${value}`;
          filterCount.set(filterKey, (filterCount.get(filterKey) || 0) + 1);
        }
      });
    });
    const topFilters = Array.from(filterCount.entries())
      .map(([filter, count]) => {
        const [filterName, filterValue] = filter.split(':');
        return { filter: filterName, value: filterValue, count };
      })
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // Search trends by hour
    const hourlyCount = new Array(24).fill(0);
    relevantEvents.forEach(event => {
      const hour = new Date(event.timestamp).getHours();
      hourlyCount[hour]++;
    });
    const searchTrends = hourlyCount.map((count, hour) => ({ hour, count }));

    // Response time percentiles
    const sortedTimes = responseTimes.sort((a, b) => a - b);
    const responseTimePercentiles = {
      p50: this.getPercentile(sortedTimes, 50),
      p90: this.getPercentile(sortedTimes, 90),
      p95: this.getPercentile(sortedTimes, 95),
      p99: this.getPercentile(sortedTimes, 99),
    };

    return {
      totalSearches,
      uniqueQueries,
      averageResponseTime: Math.round(averageResponseTime),
      cacheHitRate: Math.round(cacheHitRate * 100) / 100,
      errorRate: Math.round(errorRate * 100) / 100,
      rateLimitRate: Math.round(rateLimitRate * 100) / 100,
      topQueries,
      topFilters,
      searchTrends,
      responseTimePercentiles,
    };
  }

  getRecentSearches(limit = 50): SearchEvent[] {
    return this.events
      .slice(-limit)
      .reverse(); // Most recent first
  }

  getSearchHistory(query: string, limit = 10): SearchEvent[] {
    const normalizedQuery = query.toLowerCase().trim();
    return this.events
      .filter(event => event.query.toLowerCase().trim().includes(normalizedQuery))
      .slice(-limit)
      .reverse(); // Most recent first
  }

  private cleanup(): void {
    const oneWeekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
    const originalLength = this.events.length;
    
    this.events = this.events.filter(event => event.timestamp > oneWeekAgo);
    
    const removedCount = originalLength - this.events.length;
    if (removedCount > 0) {
      console.log(`Analytics CLEANUP: ${removedCount} old events removed`);
    }
  }

  private generateId(): string {
    return `search_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getPercentile(sortedArray: number[], percentile: number): number {
    if (sortedArray.length === 0) return 0;
    
    const index = Math.ceil((percentile / 100) * sortedArray.length) - 1;
    return sortedArray[Math.max(0, Math.min(index, sortedArray.length - 1))];
  }

  private getEmptyStats(): SearchStats {
    return {
      totalSearches: 0,
      uniqueQueries: 0,
      averageResponseTime: 0,
      cacheHitRate: 0,
      errorRate: 0,
      rateLimitRate: 0,
      topQueries: [],
      topFilters: [],
      searchTrends: new Array(24).fill(0).map((_, hour) => ({ hour, count: 0 })),
      responseTimePercentiles: { p50: 0, p90: 0, p95: 0, p99: 0 },
    };
  }

  // Graceful shutdown
  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
  }
}

export const searchAnalytics = new SearchAnalytics();
export type { SearchEvent, SearchStats };