interface RateLimitEntry {
  count: number;
  resetTime: number;
  firstRequest: number;
  lastRequest: number;
  blocked: number; // Number of blocked requests
}

interface RateLimitStats {
  activeClients: number;
  totalRequests: number;
  totalBlocked: number;
  blockRate: number;
  maxRequestsPerWindow: number;
  windowMs: number;
  averageRequestsPerClient: number;
  peakUsage: number;
}

class RateLimiter {
  private requests = new Map<string, RateLimitEntry>();
  private readonly maxRequests: number;
  private readonly windowMs: number;
  private readonly cleanupInterval: NodeJS.Timeout;
  private totalRequests = 0;
  private totalBlocked = 0;
  private peakActiveClients = 0;

  constructor(maxRequests = 60, windowMs = 60 * 1000) { // 60 requests per minute by default
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    
    // Run cleanup every 30 seconds
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 30 * 1000);
  }

  isAllowed(identifier: string): boolean {
    const now = Date.now();
    const entry = this.requests.get(identifier);
    
    this.totalRequests++;
    
    // Track peak usage
    if (this.requests.size > this.peakActiveClients) {
      this.peakActiveClients = this.requests.size;
    }

    if (!entry || now > entry.resetTime) {
      this.requests.set(identifier, {
        count: 1,
        resetTime: now + this.windowMs,
        firstRequest: now,
        lastRequest: now,
        blocked: 0,
      });
      
      console.log(`Rate Limit ALLOW: ${identifier} (1/${this.maxRequests})`);
      return true;
    }

    entry.lastRequest = now;

    if (entry.count >= this.maxRequests) {
      entry.blocked++;
      this.totalBlocked++;
      
      const resetIn = Math.ceil((entry.resetTime - now) / 1000);
      console.log(`Rate Limit BLOCK: ${identifier} (${entry.count}/${this.maxRequests}, blocked: ${entry.blocked}, reset in: ${resetIn}s)`);
      return false;
    }

    entry.count++;
    console.log(`Rate Limit ALLOW: ${identifier} (${entry.count}/${this.maxRequests})`);
    return true;
  }

  getRemainingRequests(identifier: string): number {
    const entry = this.requests.get(identifier);
    
    if (!entry || Date.now() > entry.resetTime) {
      return this.maxRequests;
    }
    
    return Math.max(0, this.maxRequests - entry.count);
  }

  getResetTime(identifier: string): number {
    const entry = this.requests.get(identifier);
    
    if (!entry || Date.now() > entry.resetTime) {
      return Date.now() + this.windowMs;
    }
    
    return entry.resetTime;
  }

  getClientInfo(identifier: string) {
    const entry = this.requests.get(identifier);
    const now = Date.now();
    
    if (!entry || now > entry.resetTime) {
      return {
        exists: false,
        remaining: this.maxRequests,
        resetTime: now + this.windowMs,
        windowStart: now,
        requests: 0,
        blocked: 0,
      };
    }
    
    return {
      exists: true,
      remaining: Math.max(0, this.maxRequests - entry.count),
      resetTime: entry.resetTime,
      windowStart: entry.firstRequest,
      requests: entry.count,
      blocked: entry.blocked,
      requestRate: entry.count / ((now - entry.firstRequest) / 1000), // requests per second
    };
  }

  cleanup(): void {
    const now = Date.now();
    let cleanedCount = 0;
    
    for (const [key, entry] of this.requests.entries()) {
      if (now > entry.resetTime) {
        this.requests.delete(key);
        cleanedCount++;
      }
    }
    
    if (cleanedCount > 0) {
      console.log(`Rate Limit CLEANUP: ${cleanedCount} expired entries removed`);
    }
  }

  getStats(): RateLimitStats {
    this.cleanup();
    
    const entries = Array.from(this.requests.values());
    const totalActiveRequests = entries.reduce((sum, entry) => sum + entry.count, 0);
    const blockRate = this.totalRequests > 0 ? (this.totalBlocked / this.totalRequests) * 100 : 0;
    const averageRequestsPerClient = entries.length > 0 ? totalActiveRequests / entries.length : 0;
    
    return {
      activeClients: this.requests.size,
      totalRequests: this.totalRequests,
      totalBlocked: this.totalBlocked,
      blockRate: Math.round(blockRate * 100) / 100,
      maxRequestsPerWindow: this.maxRequests,
      windowMs: this.windowMs,
      averageRequestsPerClient: Math.round(averageRequestsPerClient * 100) / 100,
      peakUsage: this.peakActiveClients,
    };
  }

  getDetailedStats() {
    this.cleanup();
    const stats = this.getStats();
    
    return {
      ...stats,
      clients: Array.from(this.requests.entries()).map(([identifier, entry]) => ({
        identifier: identifier.substring(0, 20) + '...', // Truncate for privacy
        requests: entry.count,
        blocked: entry.blocked,
        firstRequest: entry.firstRequest,
        lastRequest: entry.lastRequest,
        resetTime: entry.resetTime,
        remaining: Math.max(0, this.maxRequests - entry.count),
        timeToReset: Math.max(0, entry.resetTime - Date.now()),
        requestRate: entry.count / ((Date.now() - entry.firstRequest) / 1000),
      })),
    };
  }

  // Reset limits for a specific client (admin function)
  resetClient(identifier: string): boolean {
    const deleted = this.requests.delete(identifier);
    if (deleted) {
      console.log(`Rate Limit RESET: ${identifier}`);
    }
    return deleted;
  }

  // Temporarily increase limits for a client (admin function)
  increaseLimit(identifier: string, additionalRequests: number, durationMs?: number): void {
    const entry = this.requests.get(identifier);
    const now = Date.now();
    
    if (!entry || now > entry.resetTime) {
      // Create new entry with increased limit
      this.requests.set(identifier, {
        count: 0,
        resetTime: now + (durationMs || this.windowMs),
        firstRequest: now,
        lastRequest: now,
        blocked: 0,
      });
    } else {
      // Effectively increase limit by reducing count
      entry.count = Math.max(0, entry.count - additionalRequests);
    }
    
    console.log(`Rate Limit INCREASE: ${identifier} (+${additionalRequests} requests)`);
  }

  // Graceful shutdown
  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.requests.clear();
  }
}

export const searchRateLimiter = new RateLimiter(30, 60 * 1000); // 30 requests per minute for search

export function getClientIdentifier(request: Request): string {
  const forwarded = request.headers.get('x-forwarded-for');
  const realIp = request.headers.get('x-real-ip');
  const userAgent = request.headers.get('user-agent') || 'unknown';
  
  const ip = forwarded?.split(',')[0] || realIp || 'unknown';
  
  return `${ip}:${userAgent.substring(0, 50)}`;
}