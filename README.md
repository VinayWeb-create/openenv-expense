# 🚀 OpenEnv Expense Pro
### AI-Driven Autonomous Financial Simulator

OpenEnv Expense is a professional-grade Reinforcement Learning (RL) environment and full-stack dashboard for simulating and managing expenses with an AI assistant.

## ✨ Features
- **🧠 AI Assistant**: Real-time financial advice pushed via WebSockets.
- **🤖 Autonomous Mode**: Turn on the AI Agent to let it take control of your actions.
- **📊 Live Analytics**: Visual balance trends using Chart.js.
- **🌍 Dynamic Events**: Random life shocks (Pipe bursts, Lotteries) occurring periodically.
- **🎙️ Voice Control**: Voice-activated actions (Save, Food, Luxury, Skip).
- **🔒 Secure Auth**: JWT-based session management and MongoDB Atlas persistence.

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/openenv-expense.git
   cd openenv-expense
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file with your MongoDB Atlas URI:
   ```env
   MONGODB_URI=mongodb+srv://your_uri_here
   ```

4. **Run the App**:
   ```bash
   python app.py
   ```

## 📈 Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: MongoDB Atlas (Motor Driver)
- **Frontend**: Vanilla JS, CSS3, HTML5
- **Visuals**: Chart.js
- **Auth**: OAuth2/JWT (Jose, Passlib)
