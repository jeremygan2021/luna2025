import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { createProxyMiddleware } from 'http-proxy-middleware';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Proxy API requests
app.use('/api', createProxyMiddleware({
  target: 'http://luna.quant-speed.com',
  changeOrigin: true,
  pathRewrite: { '^/': '/api/' }, // Re-add /api prefix that Express strips
  onProxyReq: (proxyReq, req, res) => {
    // Log the actual path being requested on the target
    console.log(`[Proxy] ${req.method} ${req.originalUrl} -> ${proxyReq.protocol}//${proxyReq.host}${proxyReq.path}`);
  },
  // Debug: log errors
  onError: (err, req, res) => {
    console.error('Proxy Error:', err);
    res.status(500).send('Proxy Error');
  }
}));

// Serve static files from the dist directory
app.use(express.static(path.join(__dirname, 'dist')));

// Handle SPA routing: return index.html for all non-static requests
app.get(/.*/, (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});
