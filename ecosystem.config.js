module.exports = {
  apps: [
    {
      name: 'automobile-safety-api',
      script: '/home/test/testapp/venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000',
      cwd: '/home/test/testapp',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PYTHONPATH: '/home/test/testapp',
        PATH: '/home/test/testapp/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      }
    }
  ]
};