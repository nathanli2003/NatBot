import os
from flask import Flask, request, jsonify
from openai import OpenAI
import markdown

app = Flask(__name__)

# Ensure you have set your GITHUB_TOKEN in the environment variables
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

@app.route('/api/data', methods=['POST'])
def get_response():
    data = request.json
    try:
        # Get system role from data; default to a helpful assistant if not provided
        system_role = data.get('system_role', "You are a NatBot, a helpful assistant.")
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_role},
                *data['messages']
            ],
            temperature=data.get('temperature', 1.0),
            top_p=data.get('top_p', 1.0),
            max_tokens=data.get('max_tokens', 131000),
            model=model_name
        )
        
        markdown_content = response.choices[0].message.content
        html_content = markdown.markdown(markdown_content)
        return jsonify({"html": html_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ChatGPT-like Interface</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f5f5f5;
                color: #333;
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                height: 100vh;
            }
            h1 {
                color: #007bff;
                margin-bottom: 20px;
            }
            .chat-container {
                background-color: #fff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                width: 100%;
                max-width: 600px;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center; /* Center children horizontally */
            }
            textarea {
                width: calc(100% - 22px);
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ccc;
                margin-bottom: 10px;
                resize: none; /* Prevent manual resizing */
                overflow: hidden; /* Prevent scrollbars */
            }
            button {
                padding: 10px;
                border-radius: 5px;
                border: none;
                background-color: #007bff;
                color: white;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            button:hover {
                background-color: #0056b3;
            }
            #response {
                margin-top: 20px;
                border-radius: 5px;
                padding: 10px;
                background-color: #f8f9fa;
                overflow-y: auto; 
            }
            .markdown {
                color: #333; 
            }
            /* Circular Loader Styles */
            .loader {
                display: none; /* Hidden by default */
                border-radius: 50%;
                border-top: 5px solid #007bff; /* Blue color */
                border-right: 5px solid transparent; 
                width: 40px; 
                height: 40px; 
                animation: spin 1s linear infinite; 
                margin-top: 20px; /* Add some space above the loader */
            }
            @keyframes spin {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>

    <h1>Chat with NatBot</h1>
    <div class="chat-container">
        <textarea id="userInput" placeholder="Type your question here..." rows="1"></textarea>
        <button id="submitBtn">Submit</button>
        <div class="loader" id="loader"></div> <!-- Loader element -->
        <div id="response"></div>
    </div>

    <script>
        const userInput = document.getElementById('userInput');
        const loader = document.getElementById('loader');

        // Auto-resize textarea
        userInput.addEventListener('input', function () {
            this.style.height = 'auto'; // Reset height
            this.style.height = (this.scrollHeight) + 'px'; // Set new height
        });

        document.getElementById('submitBtn').addEventListener('click', async () => {
            const responseDiv = document.getElementById('response');
            
            // Clear previous response
            responseDiv.innerHTML = '';
            
            if (!userInput.value.trim()) return;

            // Show loader while waiting for response
            loader.style.display = 'block';

            try {
                const response = await fetch('/api/data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        messages: [
                            { "role": "system", "content": "You are a helpful assistant." },
                            { "role": "user", "content": userInput.value.trim() }
                        ],
                        temperature: 1.0,
                        top_p: 1.0,
                        max_tokens: 1000,
                        model: "gpt-4o"
                    })
                });

                const data = await response.json();
                
                if (response.ok) {
                    responseDiv.innerHTML = `<strong>Response:</strong> <div class="markdown">${data.html}</div>`;
                    // Retain input field value instead of clearing it
                    // userInput.value = ''; // Commented out to keep the question text
                    responseDiv.scrollTop = responseDiv.scrollHeight; // Scroll to bottom
                    
                    // Render MathJax after updating the inner HTML
                    MathJax.typeset();
                    
                } else {
                    responseDiv.innerHTML = '<strong>Error:</strong> ' + data.error;
                }
            } catch (error) {
                console.error('Error:', error);
                responseDiv.innerHTML = '<strong>Error:</strong> Unable to fetch data.';
            } finally {
                 // Hide loader after receiving the response
                 loader.style.display = 'none';
             }
        });
    </script>

    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)