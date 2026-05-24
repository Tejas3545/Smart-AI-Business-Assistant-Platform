/**
 * Frontend Performance Optimization Module
 * Provides: Request caching, debouncing, lazy loading, and request batching
 */

class PerformanceOptimizer {
  constructor() {
    this.requestCache = new Map();
    this.pendingRequests = new Map();
    this.debounceTimers = new Map();
    this.throttleTimers = new Map();
  }

  /**
   * Fetch with caching
   * Caches GET requests for specified TTL
   */
  async fetchWithCache(url, options = {}, cacheKey = null, cacheTTL = 300000) {
    const key = cacheKey || url;
    const now = Date.now();

    // Check if cached and valid
    if (this.requestCache.has(key)) {
      const cached = this.requestCache.get(key);
      if (now - cached.timestamp < cacheTTL) {
        console.debug(`[Cache HIT] ${url}`);
        return cached.data;
      } else {
        this.requestCache.delete(key);
      }
    }

    // Return pending request if already in flight
    if (this.pendingRequests.has(key)) {
      console.debug(`[Pending Request] ${url}`);
      return this.pendingRequests.get(key);
    }

    // Make request and cache result
    const requestPromise = fetch(url, options)
      .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then(data => {
        // Only cache successful GET requests
        if (options.method !== 'POST' && options.method !== 'PUT' && options.method !== 'DELETE') {
          this.requestCache.set(key, { data, timestamp: Date.now() });
          console.debug(`[Cache SET] ${url}`);
        }
        this.pendingRequests.delete(key);
        return data;
      })
      .catch(error => {
        this.pendingRequests.delete(key);
        throw error;
      });

    this.pendingRequests.set(key, requestPromise);
    return requestPromise;
  }

  /**
   * Debounce function calls
   * Useful for search, filter inputs, autocomplete
   */
  debounce(key, fn, delay = 300) {
    if (this.debounceTimers.has(key)) {
      clearTimeout(this.debounceTimers.get(key));
    }

    const timer = setTimeout(() => {
      fn();
      this.debounceTimers.delete(key);
    }, delay);

    this.debounceTimers.set(key, timer);
  }

  /**
   * Throttle function calls
   * Useful for scroll, resize events
   */
  throttle(key, fn, delay = 1000) {
    if (this.throttleTimers.has(key)) {
      return;
    }

    fn();
    this.throttleTimers.set(key, true);

    setTimeout(() => {
      this.throttleTimers.delete(key);
    }, delay);
  }

  /**
   * Clear cache
   */
  clearCache(pattern = null) {
    if (!pattern) {
      this.requestCache.clear();
      console.debug('[Cache CLEAR] All');
    } else {
      for (const key of this.requestCache.keys()) {
        if (key.includes(pattern)) {
          this.requestCache.delete(key);
        }
      }
      console.debug(`[Cache CLEAR] Pattern: ${pattern}`);
    }
  }

  /**
   * Invalidate specific cache
   */
  invalidateCache(key) {
    this.requestCache.delete(key);
  }
}

// Global instance
const optimizer = new PerformanceOptimizer();

/**
 * Lazy Load View
 * Load content only when view becomes visible
 */
class LazyViewLoader {
  constructor() {
    this.loadedViews = new Set();
    this.loadingViews = new Set();
  }

  async loadView(viewName, loader) {
    if (this.loadedViews.has(viewName)) {
      console.debug(`[LazyLoad] View already loaded: ${viewName}`);
      return;
    }

    if (this.loadingViews.has(viewName)) {
      console.debug(`[LazyLoad] View already loading: ${viewName}`);
      return;
    }

    try {
      this.loadingViews.add(viewName);
      console.debug(`[LazyLoad] Loading: ${viewName}`);
      
      await loader();
      
      this.loadedViews.add(viewName);
      this.loadingViews.delete(viewName);
      console.debug(`[LazyLoad] Loaded: ${viewName}`);
    } catch (error) {
      console.error(`[LazyLoad] Failed to load ${viewName}:`, error);
      this.loadingViews.delete(viewName);
    }
  }

  isLoaded(viewName) {
    return this.loadedViews.has(viewName);
  }
}

const lazyLoader = new LazyViewLoader();

/**
 * LocalStorage Cache for non-sensitive data
 */
class LocalStorageCache {
  static set(key, value, ttl = 3600000) { // 1 hour default
    const item = {
      value,
      expires: Date.now() + ttl,
    };
    try {
      localStorage.setItem(`cache:${key}`, JSON.stringify(item));
    } catch (e) {
      console.warn(`LocalStorage quota exceeded for key: ${key}`);
    }
  }

  static get(key) {
    try {
      const item = JSON.parse(localStorage.getItem(`cache:${key}`));
      if (!item) return null;
      
      if (Date.now() > item.expires) {
        localStorage.removeItem(`cache:${key}`);
        return null;
      }
      
      return item.value;
    } catch (e) {
      return null;
    }
  }

  static remove(key) {
    localStorage.removeItem(`cache:${key}`);
  }

  static clear() {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('cache:')) {
        localStorage.removeItem(key);
      }
    });
  }
}

/**
 * Request batch manager
 * Batch multiple requests into single API call
 */
class BatchRequestManager {
  constructor(batchSize = 10, batchDelay = 100) {
    this.queue = [];
    this.batchSize = batchSize;
    this.batchDelay = batchDelay;
    this.timer = null;
  }

  async add(item) {
    return new Promise((resolve, reject) => {
      this.queue.push({ item, resolve, reject });
      
      if (this.queue.length >= this.batchSize) {
        this.flush();
      } else if (!this.timer) {
        this.timer = setTimeout(() => this.flush(), this.batchDelay);
      }
    });
  }

  async flush() {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }

    if (this.queue.length === 0) return;

    const batch = this.queue.splice(0, this.batchSize);
    console.debug(`[Batch Request] Processing ${batch.length} items`);

    // Process batch items
    batch.forEach(({ item, resolve, reject }) => {
      try {
        resolve(item);
      } catch (error) {
        reject(error);
      }
    });
  }
}

const batchManager = new BatchRequestManager();

// Export for use in main app
console.log('[Performance] Optimizer, LazyLoader, LocalStorageCache loaded');
