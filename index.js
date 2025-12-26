#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

const serverPath = path.join(__dirname, 'src/arch_ops_server/omega_engine.py');

// 手机/服务器环境自适应启动逻辑
const cmd = 'uv';
const args = ['run', 'python', serverPath];

const child = spawn(cmd, args, {
    stdio: 'inherit',
    shell: true,
    env: { ...process.env, PYTHONPATH: path.join(__dirname, 'src') }
});

child.on('error', (err) => {
    console.error('Failed to start Omega Engine:', err.message);
    process.exit(1);
});
