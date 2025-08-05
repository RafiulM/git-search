interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
  hits: number;
  lastAccessed: number;
}

interface CacheStats {
  size: number;
  totalHits: number;
  totalMisses: number;
  hitRate: number;
  oldestEntry?: number;
  newestEntry?: number;
  totalMemoryUsage: number;
  averageEntrySize: number;
}

class InMemoryCache {
  private cache = new Map<string, CacheEntry<any>>();
  private readonly defaultTTL = 5 * 60 * 1000; // 5 minutes
  private readonly maxSize = 1000; // Maximum cache entries
  private readonly maxMemoryMB = 100; // Maximum memory usage in MB
  private totalHits = 0;
  private totalMisses = 0;
  private cleanupInterval: NodeJS.Timeout;

  constructor() {
    // Run cleanup every 2 minutes
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 2 * 60 * 1000);
  }

  set<T>(key: string, data: T, ttl?: number): void {
    const now = Date.now();
    const expiration = ttl || this.defaultTTL;
    
    // Check if we need to evict entries
    this.evictIfNeeded();
    
    const entry: CacheEntry<T> = {
      data,
      timestamp: now,
      expiresAt: now + expiration,
      hits: 0,
      lastAccessed: now,
    };
    
    this.cache.set(key, entry);
    
    // Log cache set operation
    console.log(`Cache SET: ${key} (TTL: ${expiration}ms, Size: ${this.cache.size})`);
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) {
      this.totalMisses++;
      console.log(`Cache MISS: ${key}`);
      return null;
    }
    
    const now = Date.now();
    
    if (now > entry.expiresAt) {
      this.cache.delete(key);
      this.totalMisses++;
      console.log(`Cache EXPIRED: ${key}`);
      return null;
    }
    
    // Update access statistics
    entry.hits++;
    entry.lastAccessed = now;
    this.totalHits++;
    
    console.log(`Cache HIT: ${key} (hits: ${entry.hits})`);
    return entry.data as T;
  }

  has(key: string): boolean {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return false;
    }
    
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return false;
    }
    
    return true;
  }

  delete(key: string): boolean {
    const deleted = this.cache.delete(key);
    if (deleted) {
      console.log(`Cache DELETE: ${key}`);
    }
    return deleted;
  }

  clear(): void {
    const size = this.cache.size;
    this.cache.clear();
    this.totalHits = 0;
    this.totalMisses = 0;
    console.log(`Cache CLEAR: ${size} entries removed`);
  }

  size(): number {
    this.cleanup();
    return this.cache.size;
  }

  private cleanup(): void {
    const now = Date.now();
    let expiredCount = 0;
    
    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiresAt) {
        this.cache.delete(key);
        expiredCount++;
      }
    }
    
    if (expiredCount > 0) {
      console.log(`Cache CLEANUP: ${expiredCount} expired entries removed`);
    }
  }

  private evictIfNeeded(): void {
    // Check size limit
    if (this.cache.size >= this.maxSize) {
      this.evictLeastRecentlyUsed(Math.floor(this.maxSize * 0.1)); // Remove 10%
    }
    
    // Check memory limit
    const memoryUsage = this.getMemoryUsageMB();
    if (memoryUsage > this.maxMemoryMB) {
      this.evictLeastRecentlyUsed(Math.floor(this.cache.size * 0.2)); // Remove 20%
    }
  }

  private evictLeastRecentlyUsed(count: number): void {
    // Sort entries by last accessed time (oldest first)
    const sortedEntries = Array.from(this.cache.entries())
      .sort(([, a], [, b]) => a.lastAccessed - b.lastAccessed);
    
    let evictedCount = 0;
    for (let i = 0; i < Math.min(count, sortedEntries.length); i++) {
      const [key] = sortedEntries[i];
      this.cache.delete(key);
      evictedCount++;
    }
    
    if (evictedCount > 0) {
      console.log(`Cache EVICTION: ${evictedCount} LRU entries removed`);
    }
  }

  private getMemoryUsageMB(): number {
    let totalSize = 0;
    for (const [key, entry] of this.cache.entries()) {
      totalSize += key.length * 2; // Unicode characters are 2 bytes
      totalSize += JSON.stringify(entry.data).length * 2;
      totalSize += 64; // Approximate overhead per entry
    }
    return totalSize / (1024 * 1024); // Convert to MB
  }

  getStats(): CacheStats {
    this.cleanup();
    
    const entries = Array.from(this.cache.values());
    const totalRequests = this.totalHits + this.totalMisses;
    const hitRate = totalRequests > 0 ? (this.totalHits / totalRequests) * 100 : 0;
    
    const timestamps = entries.map(e => e.timestamp);
    const memoryUsage = this.getMemoryUsageMB();
    
    return {
      size: this.cache.size,
      totalHits: this.totalHits,
      totalMisses: this.totalMisses,
      hitRate: Math.round(hitRate * 100) / 100,
      oldestEntry: timestamps.length > 0 ? Math.min(...timestamps) : undefined,
      newestEntry: timestamps.length > 0 ? Math.max(...timestamps) : undefined,
      totalMemoryUsage: Math.round(memoryUsage * 100) / 100,
      averageEntrySize: entries.length > 0 ? Math.round((memoryUsage * 1024 * 1024) / entries.length) : 0,
    };
  }

  getDetailedStats() {
    this.cleanup();
    const stats = this.getStats();
    
    return {
      ...stats,
      entries: Array.from(this.cache.entries()).map(([key, entry]) => ({
        key,
        timestamp: entry.timestamp,
        expiresAt: entry.expiresAt,
        hits: entry.hits,
        lastAccessed: entry.lastAccessed,
        dataSize: JSON.stringify(entry.data).length,
        ttl: entry.expiresAt - Date.now(),
        age: Date.now() - entry.timestamp,
      })),
      memoryLimits: {
        maxSize: this.maxSize,
        maxMemoryMB: this.maxMemoryMB,
        currentMemoryMB: this.getMemoryUsageMB(),
      }
    };
  }

  // Graceful shutdown
  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.clear();
  }
}

export const searchCache = new InMemoryCache();

export function createCacheKey(query: string, params: Record<string, any>): string {
  const sortedParams = Object.keys(params)
    .sort()
    .reduce((result, key) => {
      if (params[key] !== undefined && params[key] !== null) {
        result[key] = params[key];
      }
      return result;
    }, {} as Record<string, any>);

  return `search:${query}:${JSON.stringify(sortedParams)}`;
}