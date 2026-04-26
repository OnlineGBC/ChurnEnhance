from flask import Blueprint, render_template, request, jsonify, session
from config.settings import Config

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/")
def index():
    return render_template("chat.html", config=Config)


@chat_bp.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    llm_model = session.get("llm_model", Config.DEFAULT_LLM)

    try:
        from agents.orchestrator import run_chat_query
        response = run_chat_query(message, llm_model)
        return jsonify({"response": response, "model": llm_model})
    except Exception as e:
        return jsonify({"error": str(e), "response": f"Error: {str(e)}"}), 500
