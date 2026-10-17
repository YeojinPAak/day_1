from flask import Blueprint, request, jsonify
import random
from groq import Groq

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

#Groq API 설정
client = Groq(api_key='YOUR_GROQ_API_KEY')

def get_response(user_input):
    """사용자 입력에 대한 응답 반환"""
    user_input = user_input.lower().strip()
    
    # Groq 모델을 사용하여 응답 생성
    try:
        response = client.chat.completions.create(
            messages=[
                {"role":"user","content" : user_input}
            ],
            model="mixtral-8x7b-v0.1"  # 원하는 모델로 변경 가능
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq API 오류: {e}")
        return "죄송합니다, 지금은 답변할 수 없습니다."

@chatbot_bp.route('/ask', methods=['POST'])
def ask():
    """챗봇에 질문"""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': '메시지를 입력해주세요'}), 400
    
    response = get_response(user_message)
    return jsonify({
        'user_message': user_message,
        'bot_response': response
    })

@chatbot_bp.route('/chat', methods=['GET'])
def chat():
    """챗봇 페이지"""
    return """
    <h1>AI 챗봇</h1>
    <div id="chat-box" style="border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 10px;">
    </div>
    <input type="text" id="user-input" placeholder="질문을 입력하세요..." style="width: 80%; padding: 8px;">
    <button onclick="sendMessage()" style="padding: 8px 15px;">전송</button>
    
    <script>
    function sendMessage() {
        const userInput = document.getElementById('user-input').value;
        if (!userInput) return;
        
        // 사용자 메시지 표시
        const chatBox = document.getElementById('chat-box');
        chatBox.innerHTML += '<p><strong>You:</strong> ' + userInput + '</p>';
        
        // 봇 응답 받기
        fetch('/chatbot/ask', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: userInput})
        })
        .then(response => response.json())
        .then(data => {
            chatBox.innerHTML += '<p><strong>Bot:</strong> ' + data.bot_response + '</p>';
            chatBox.scrollTop = chatBox.scrollHeight;
        });
        
        document.getElementById('user-input').value = '';
    }
    
    // Enter 키로도 전송 가능
    document.getElementById('user-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
    </script>
    """
