module.exports = {
  apps: [
    {
      name: 'automobile-safety-api',
      script: 'venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000',
      cwd: '/home/test/testapp',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      min_uptime: '30s',
      max_restarts: 5,
      restart_delay: 5000,
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: '/home/test/testapp'
      }
    }
  ]
};
