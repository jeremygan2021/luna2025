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
  pathRewrite: {
    // Keep /api prefix if the target expects it, or remove it if not.
    // Based on the curl example: http://luna.quant-speed.com/api/todos/
    // It seems the target HAS /api. So we don't need to rewrite path if we forward /api...
    // But wait, if I request /api/todos, it goes to target/api/todos. Correct.
  },
  onProxyReq: (proxyReq, req, res) => {
    // Optional: Log proxy requests
    // console.log(`Proxying ${req.method} ${req.path} to ${proxyReq.host}`);
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
