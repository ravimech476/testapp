module.exports = {
  apps: [
    {
      name: 'automobile-safety-api',
      script: 'uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000',
      cwd: 'D:/PROJECTS/testapp',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      
      // Environment variables
      env: {
        NODE_ENV: 'development',
        PORT: 8000,
        PYTHONPATH: 'D:/PROJECTS/testapp'
      },
      
      env_production: {
        NODE_ENV: 'production',
        PORT: 8000,
        PYTHONPATH: 'D:/PROJECTS/testapp'
      },
      
      env_staging: {
        NODE_ENV: 'staging',
        PORT: 8001,
        PYTHONPATH: 'D:/PROJECTS/testapp'
      },
      
      // Logging
      log_file: './logs/combined.log',
      out_file: './logs/out.log',
      error_file: './logs/error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      
      // Process management
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
      
      // Health monitoring
      health_check_url: 'http://localhost:8000/api/health',
      health_check_grace_period: 3000,
      
      // Advanced settings
      interpreter: 'none',
      kill_timeout: 5000,
      listen_timeout: 8000,
      
      // Source map and error handling
      source_map_support: false,
      disable_source_map_support: true
    },
    
    // Production configuration with Gunicorn
    {
      name: 'automobile-safety-api-prod',
      script: 'gunicorn',
      args: 'main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120',
      cwd: 'D:/PROJECTS/testapp',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      
      env_production: {
        NODE_ENV: 'production',
        PYTHONPATH: 'D:/PROJECTS/testapp',
        WORKERS: 4
      },
      
      // Logging for production
      log_file: './logs/prod-combined.log',
      out_file: './logs/prod-out.log',
      error_file: './logs/prod-error.log',
      
      // Health monitoring
      health_check_url: 'http://localhost:8000/api/health',
      health_check_grace_period: 5000
    }
  ],
  
  // Deployment configuration
  deploy: {
    production: {
      user: 'ubuntu',
      host: ['your-server-ip'],
      ref: 'origin/main',
      repo: 'your-git-repo-url',
      path: '/var/www/automobile-safety-api',
      'pre-deploy-local': '',
      'post-deploy': 'pip install -r requirements.txt && mkdir -p logs && mkdir -p uploads && pm2 reload ecosystem.config.js --env production',
      'pre-setup': 'mkdir -p /var/www/automobile-safety-api'
    },
    
    staging: {
      user: 'ubuntu',
      host: ['your-staging-server-ip'],
      ref: 'origin/develop',
      repo: 'your-git-repo-url',
      path: '/var/www/automobile-safety-api-staging',
      'post-deploy': 'pip install -r requirements.txt && mkdir -p logs && mkdir -p uploads && pm2 reload ecosystem.config.js --env staging'
    }
  }
};
