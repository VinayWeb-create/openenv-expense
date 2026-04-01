from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from env.expense_env import ExpenseEnv
import auth
import database
from datetime import timedelta
import os

app = FastAPI(title="OpenEnv Expense Pro", description="AI Expense Management with Persistence and Security")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- Security & Auth Endpoints ---

@app.post("/signup")
async def signup(form_data: OAuth2PasswordRequestForm = Depends()):
    existing_user = await database.users_collection.find_one({"username": form_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(form_data.password)
    user_dict = {"username": form_data.username, "hashed_password": hashed_password}
    await database.users_collection.insert_one(user_dict)
    return {"message": "User created successfully"}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await database.users_collection.find_one({"username": form_data.username})
    if not user or not auth.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except auth.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await database.users_collection.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# --- Real-Time Sync (WebSockets) ---

@app.websocket("/ws/suggestions")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Server could push events here independently
            await websocket.receive_text() # keep connection alive
    except WebSocketDisconnect:
        pass

# --- Alert Mock (Email Simulation) ---

def send_alert_mock(user_id: str, message: str):
    """ Mocks an email notification for critical events. """
    print(f"📧 [EMAIL ALERT TO {user_id}]: {message}")

# --- Smart AI Suggestion Engine ---

def get_ai_suggestion(balance: float, day: int):
    """ Generates real-time AI advice based on current state. """
    if balance < 1000:
        return "⚠️ CRITICAL: Balance dangerously low! Prioritize 'SAVE' actions only."
    elif day > 25 and balance > 4000:
        return "💎 PERFORMANCE: You have over 40-day runway. Try 'SKIP' or 'SAVE' to finish strong."
    elif balance > 7000:
        return "💰 GROWTH: Strong balance! Interest rates are working in your favor."
    else:
        return "💡 ADVICE: Daily spending is moderate. Maintain current strategy."

# --- Managed Environments ---

# Cache of active environment instances
user_envs = {}

def get_env_for_user(username: str):
    if username not in user_envs:
        user_envs[username] = ExpenseEnv()
    return user_envs[username]

@app.get("/reset")
async def reset_env(user: dict = Depends(get_current_user)):
    username = user["username"]
    env = get_env_for_user(username)
    state = env.reset()
    
    # Persist reset state to MongoDB
    await database.save_user_state(username, state, env.day, env.balance)
    return {"message": "Environment reset.", "state": state}

@app.get("/step/{action}")
async def step(action: int, user: dict = Depends(get_current_user)):
    username = user["username"]
    env = get_env_for_user(username)
    
    if action not in [0, 1, 2, 3]: # Food, Save, Skip, Luxury
        raise HTTPException(status_code=400, detail="Invalid action.")
    
    state, reward, done, event_msg = env.step(action)
    suggestion = get_ai_suggestion(env.balance, env.day)
    
    if event_msg: suggestion = event_msg
    
    # Check for Alert Condition
    if env.balance < 500:
        send_alert_mock(username, "CRITICAL ALERT: Balance is below $500!")

    # Persist action and state to MongoDB
    await database.save_user_state(username, state, env.day, env.balance)
    await database.add_history_entry(username, action, reward, env.balance, env.day)
    
    return {"state": state, "reward": reward, "done": done, "suggestion": suggestion}

@app.post("/autonomous-step")
async def autonomous_step(user: dict = Depends(get_current_user)):
    """ AI takes a step based on current logic. """
    username = user["username"]
    env = get_env_for_user(username)
    # Simple Optimal: Save if low, Food if okay, Skip if rich
    action = 1 if env.balance < 2000 else (0 if env.balance < 4000 else 2)
    return await step(action, user)

@app.get("/history")
async def view_history(user: dict = Depends(get_current_user)):
    """ Retrieves entire transaction history from MongoDB. """
    username = user["username"]
    cursor = database.env_history_collection.find({"user_id": username}).sort("day", 1)
    history = await cursor.to_list(length=100)
    # Convert MongoDB IDs to strings
    for entry in history: entry["_id"] = str(entry["_id"])
    return history

@app.get("/leaderboard")
async def get_leaderboard():
    """ Global performance board. """
    cursor = database.env_state_collection.find().sort("balance", -1)
    leaderboard = await cursor.to_list(length=10)
    return [{"user": l["user_id"], "balance": round(l["balance"])} for l in leaderboard]

@app.post("/voice")
async def process_voice(data: dict, user: dict = Depends(get_current_user)):
    """ Mocks Voice processing from Speech-to-Text. """
    text = data.get("text", "").lower()
    if "save" in text: return await step(1, user)
    if "food" in text: return await step(0, user)
    if "luxury" in text: return await step(3, user)
    if "skip" in text: return await step(2, user)
    return {"message": f"Couldn't understand '{text}'"}

@app.get("/state")
async def get_state(user: dict = Depends(get_current_user)):
    username = user["username"]
    env = get_env_for_user(username)
    return env.state()

# --- Frontend Serving ---

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/index.css")
async def css():
    return FileResponse("index.css")

@app.get("/index.js")
async def js():
    return FileResponse("index.js")

if __name__ == "__main__":
    import uvicorn
    # Important: Use 0.0.0.0 and PORT from Render
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
