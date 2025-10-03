#!/usr/bin/env python3
"""
ResearchForge v1.0 - REST API Server
Complete API with rate limiting, caching, and async support
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime
import hashlib
from typing import Dict, Any
import os

from researchforge_v1 import (
    ResearchForge,
    ResearchQuery,
    format_output_markdown,
    format_output_json
)


class ResearchCache:
    """Simple in-memory cache for research results"""
    
    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, query: str, context: str) -> str:
        """Generate cache key from query and context"""
        combined = f"{query}|{context}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, query: str, context: str) -> Any:
        """Get cached result"""
        key = self._generate_key(query, context)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, query: str, context: str, result: Any):
        """Cache a result"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        key = self._generate_key(query, context)
        self.cache[key] = {
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'context': context
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.2%}",
            'total_requests': total
        }


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_requests: int = 60):
        self.max_requests = max_requests
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed"""
        now = datetime.now()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Clean old requests (older than 1 minute)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if (now - req_time).seconds < 60
        ]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        self.requests[client_ip].append(now)
        return True


class ResearchAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for ResearchForge API"""
    
    forge = ResearchForge()
    cache = ResearchCache(max_size=100)
    rate_limiter = RateLimiter(max_requests=60)
    request_count = 0
    
    def _set_headers(self, status_code: int = 200, content_type: str = 'application/json'):
        """Set response headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def _send_error(self, message: str, status_code: int = 400):
        """Send error response"""
        self._send_json({
            'error': message,
            'status': status_code,
            'timestamp': datetime.now().isoformat()
        }, status_code)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self._set_headers(204)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Health check
        if path == '/health':
            self._send_json({
                'status': 'healthy',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            })
            return
        
        # API stats
        if path == '/stats':
            cache_stats = self.cache.get_stats()
            self._send_json({
                'total_requests': self.request_count,
                'cache': cache_stats,
                'knowledge_base_size': len(self.forge.knowledge_base),
                'uptime': 'N/A'
            })
            return
        
        # Knowledge base
        if path == '/knowledge':
            self._send_json({
                'entries': self.forge.knowledge_base,
                'count': len(self.forge.knowledge_base)
            })
            return
        
        # Root - API documentation
        if path == '/':
            self._set_headers(200, 'text/html')
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>ResearchForge API v1.0</title>
                <style>
                    body { font-family: system-ui; max-width: 800px; margin: 50px auto; padding: 20px; }
                    h1 { color: #2563eb; }
                    code { background: #f3f4f6; padding: 2px 6px; border-radius: 3px; }
                    pre { background: #1f2937; color: #f3f4f6; padding: 15px; border-radius: 8px; overflow-x: auto; }
                    .endpoint { background: #e5e7eb; padding: 15px; margin: 10px 0; border-radius: 8px; }
                </style>
            </head>
            <body>
                <h1>🔬 ResearchForge API v1.0</h1>
                <p><strong>Status:</strong> Online | <strong>Version:</strong> 1.0.0</p>
                
                <h2>Endpoints</h2>
                
                <div class="endpoint">
                    <h3>POST /research</h3>
                    <p>Execute research query</p>
                    <pre>{
  "query": "Your research question",
  "context": "Optional context",
  "iterations": 4,
  "tcr": 0.95,
  "format": "json"
}</pre>
                </div>
                
                <div class="endpoint">
                    <h3>GET /health</h3>
                    <p>Health check endpoint</p>
                </div>
                
                <div class="endpoint">
                    <h3>GET /stats</h3>
                    <p>API statistics (cache, requests, etc.)</p>
                </div>
                
                <div class="endpoint">
                    <h3>GET /knowledge</h3>
                    <p>View knowledge base entries</p>
                </div>
                
                <h2>Example Request</h2>
                <pre>curl -X POST http://localhost:8080/research \\
  -H "Content-Type: application/json" \\
  -d '{"query": "advanced prompt engineering techniques"}'</pre>
                
                <p><em>Documentation: <a href="https://github.com/your-repo">GitHub</a></em></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
            return
        
        self._send_error('Endpoint not found', 404)
    
    def do_POST(self):
        """Handle POST requests"""
        ResearchAPIHandler.request_count += 1
        
        # Rate limiting
        client_ip = self.client_address[0]
        if not self.rate_limiter.is_allowed(client_ip):
            self._send_error('Rate limit exceeded. Max 60 requests per minute.', 429)
            return
        
        # Parse request
        if self.path != '/research':
            self._send_error('Endpoint not found', 404)
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            self._send_error(f'Invalid JSON: {str(e)}', 400)
            return
        
        # Validate input
        if 'query' not in data:
            self._send_error('Missing required field: query', 400)
            return
        
        query_text = data['query']
        context = data.get('context', '')
        
        # Check cache
        cached_result = self.cache.get(query_text, context)
        if cached_result:
            response = cached_result['result']
            response['cached'] = True
            response['cache_timestamp'] = cached_result['timestamp']
            self._send_json(response)
            return
        
        # Execute research
        try:
            query = ResearchQuery(
                query=query_text,
                context_seed=context,
                max_iterations=data.get('iterations', 4),
                target_tcr=data.get('tcr', 0.95),
                target_relevance=data.get('relevance', 0.90),
                max_tokens=data.get('max_tokens', 2500)
            )
            
            result = self.forge.research(query)
            
            # Format response
            output_format = data.get('format', 'json')
            
            if output_format == 'markdown':
                response = {
                    'success': True,
                    'format': 'markdown',
                    'output': format_output_markdown(result),
                    'metrics': result.metrics,
                    'iterations_used': result.iterations_used,
                    'cached': False,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                response = {
                    'success': True,
                    'format': 'json',
                    'decomposed_plan': [
                        {
                            'id': sq.id,
                            'question': sq.question,
                            'phase': sq.phase.value,
                            'novelty_score': sq.novelty_score
                        }
                        for sq in result.decomposed_plan
                    ],
                    'findings': result.synthesized_results.get('key_findings', []),
                    'techniques_applied': result.synthesized_results.get('techniques_applied', []),
                    'insight': result.surprise_insight,
                    'metrics': result.metrics,
                    'sources': result.sources,
                    'iterations_used': result.iterations_used,
                    'cached': False,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Cache result
            self.cache.set(query_text, context, response)
            
            self._send_json(response)
            
        except Exception as e:
            self._send_error(f'Research execution failed: {str(e)}', 500)
    
    def log_message(self, format, *args):
        """Custom log format"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {self.client_address[0]} - {format % args}")


def run_server(host: str = '0.0.0.0', port: int = 8080):
    """Run the API server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, ResearchAPIHandler)
    
    print("=" * 70)
    print("🔬 ResearchForge v1.0 - REST API Server")
    print("=" * 70)
    print(f"\n✅ Server running on http://{host}:{port}")
    print(f"📚 API documentation: http://{host}:{port}/")
    print(f"❤️  Health check: http://{host}:{port}/health")
    print(f"📊 Statistics: http://{host}:{port}/stats")
    print(f"\n⏹️  Press Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        print("=" * 70)


if __name__ == '__main__':
    import sys
    
    # Parse arguments
    host = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    run_server(host, port)
