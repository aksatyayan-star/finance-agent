import os
import uuid
from flask import Flask, request, jsonify

# We need to import the agent to interact with it.
# This assumes the agent object can be imported and used directly.
from src.finance_buddy.agent.agent import root_agent

app = Flask(__name__)

# A simple in-memory store for conversation sessions.
# In a real production system, this would be a database like Redis or Firestore.
conversation_sessions = {}

@app.route('/chat', methods=['POST'])
def chat_handler():
    """
    Handles incoming chat messages from users.
    Expects a JSON body with 'session_id' (optional) and 'message'.
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid request. 'message' is required."}), 400

    session_id = data.get('session_id')
    user_message = data['message']

    # Get or create the conversation session
    if session_id and session_id in conversation_sessions:
        session = conversation_sessions[session_id]
    else:
        # A new conversation starts
        session_id = str(uuid.uuid4())
        # The ADK agent's chat method likely handles history internally,
        # but we might need to initialize it or store it if the library requires.
        # For now, we'll just call the chat method.
        session = root_agent.chat() # This is a guess at the ADK API
        conversation_sessions[session_id] = session

    try:
        # This is where the integration with the agent happens.
        # We send the user's message to the agent's chat session.
        agent_reply = session.send(user_message)

        # The response from session.send might be an iterator for streaming,
        # or a final object. We'll assume it's a final object for now.
        # We need to extract the text response.
        # This is a placeholder for the actual response extraction logic.
        response_message = ""
        for chunk in agent_reply:
            if chunk.text:
                response_message += chunk.text

    except Exception as e:
        print(f"Error during agent interaction: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

    return jsonify({
        "reply": response_message,
        "session_id": session_id
    })

if __name__ == '__main__':
    # This is for local testing only. Gunicorn will be used in production.
    # The PORT environment variable is used by Google Cloud Run.
    app.run(debug=True, port=int(os.environ.get("PORT", 8080)))
