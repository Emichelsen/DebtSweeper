import os
import time
from flask import Flask, render_template, send_from_directory, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Set up OpenAI in a way that prevents initialization errors
# We'll create the client only when needed, not at module import time
has_openai = False
try:
    from openai import OpenAI
    has_openai = True
except ImportError:
    pass  # OpenAI not installed

def refactor_snippet(snippet, system_prompt, retries=3):
    """
    Refactor a code snippet using GPT-4o-mini.
    Includes retry logic with exponential backoff.
    """
    if not has_openai:
        return "OpenAI library not installed. Please install with: pip install openai"

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OpenAI API key not set. Please set the OPENAI_API_KEY environment variable."

    for attempt in range(retries):
        try:
            # Create client for each request to avoid initialization issues
            # Using a minimal configuration to avoid compatibility problems
            client = None
            try:
                # Try to initialize with default parameters
                client = OpenAI(api_key=api_key)
            except TypeError:
                # If that fails, try to monkey-patch httpx.Client to ignore 'proxies'
                import httpx
                original_client = httpx.Client

                # Create a wrapper that filters out problematic kwargs
                def patched_client_init(*args, **kwargs):
                    # Remove the problematic 'proxies' parameter if present
                    if 'proxies' in kwargs:
                        del kwargs['proxies']
                    return original_client(*args, **kwargs)

                # Replace the client constructor temporarily
                httpx.Client = patched_client_init
                try:
                    client = OpenAI(api_key=api_key)
                finally:
                    # Restore original constructor
                    httpx.Client = original_client

            if not client:
                return "Failed to initialize OpenAI client due to compatibility issues."

            # Make the API call
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": snippet}
                ],
                temperature=0.2,
                max_tokens=4096,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            return response.choices[0].message.content
        except Exception as e:
            # Handle all exceptions in a generic way for robustness
            if "RateLimitError" in str(type(e)):
                backoff = 2 ** attempt
                print(f"Rate limit hit, retrying in {backoff}s...")
                time.sleep(backoff)
            else:
                print(f"API error: {str(e)}")
                raise

    # If we've exhausted all retries
    raise RuntimeError("Max retries reached for LLM refactor")

@app.route('/')
def index():
    """Dashboard homepage with Debt Knowledge Graph."""
    return render_template('index.html')

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    """Handle repository scanning and display results."""
    if request.method == 'POST':
        # For demo purposes, just return mock data
        return jsonify({
            'repo_score': 0.4,
            'total_debt_items': 15,
            'total_loc': 1200,
            'items_by_type': {
                'long_function': 5,
                'high_complexity': 7,
                'code_duplication': 3
            }
        })
    
    # GET request - show upload form
    return render_template('scan.html')

@app.route('/generate-fixes', methods=['POST'])
def generate_fixes():
    """
    Generate fixes for technical debt items using GPT-4o-mini.
    Expects a JSON payload with code snippets that need refactoring.
    """
    data = request.json
    snippets = data.get('snippets', [])
    fixes = []
    
    system_prompt = """
    You are a senior Python developer specializing in code refactoring to eliminate technical debt.
    Your task is to refactor the provided code snippet to:
    1. Reduce complexity by breaking down long functions
    2. Improve readability with better variable names and comments
    3. Eliminate code duplication through proper abstraction
    4. Apply appropriate design patterns
    5. Ensure PEP 8 compliance
    
    Provide ONLY the refactored code as your response, with no explanations or annotations.
    The refactored code should maintain the same functionality but with better structure and readability.
    """
    
    # Process each snippet
    for snippet in snippets:
        try:
            refactored_code = refactor_snippet(snippet['code'], system_prompt)
            fixes.append({
                'id': snippet['id'],
                'original': snippet['code'],
                'refactored': refactored_code,
                'status': 'success'
            })
        except Exception as e:
            # If refactoring fails, include the error in the response
            fixes.append({
                'id': snippet['id'],
                'original': snippet['code'],
                'status': 'error',
                'error': str(e)
            })
    
    return jsonify({
        'fixes': fixes
    })

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Use port provided by environment variable or default to 5051
    port = int(os.environ.get("PORT", 5051))
    app.run(host='0.0.0.0', port=port, debug=True)