// Frontend configuration settings

export const config = {
  // Rate limiting configuration
  analysis: {
    // Polling interval in milliseconds for checking analysis status
    statusPollInterval: 5000, // 5 seconds
    
    // Auto-refresh settings for pending analyses
    autoRefresh: {
      enabled: true,
      interval: 5000 // 5 seconds
    }
  },
  
  // API settings
  api: {
    // Retry configuration for failed requests
    retry: {
      maxAttempts: 3,
      delay: 1000 // 1 second
    }
  }
};

// Type definitions for configuration
export interface AnalysisConfig {
  statusPollInterval: number;
  autoRefresh: {
    enabled: boolean;
    interval: number;
  };
}

export interface ApiConfig {
  retry: {
    maxAttempts: number;
    delay: number;
  };
}

export interface AppConfig {
  analysis: AnalysisConfig;
  api: ApiConfig;
}
