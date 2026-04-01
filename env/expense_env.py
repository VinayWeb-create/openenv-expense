import random

class ExpenseEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        """Initializes the environment state."""
        self.balance = 5000
        self.day = 1
        self.max_days = 30
        return self.state()

    def state(self):
        """Returns the current state: (balance, day)."""
        return {"balance": self.balance, "day": self.day}

    def step(self, action):
        """
        Takes an action and returns (state, reward, done).
        Actions:
        0 = Spend (random 100-500)
        1 = Save
        2 = Skip
        """
        reward = 0
        done = False

        if action == 0:  # Food/Essential Spend
            amount = random.randint(50, 150)
            self.balance -= amount
            reward = -0.1
        elif action == 1:  # Save
            reward = 1.0
        elif action == 2:  # Skip
            reward = 0.2
        elif action == 3:  # Luxury Spend
            amount = random.randint(300, 800)
            self.balance -= amount
            reward = -1.0

        # --- Advanced Financial Logic ---
        # 1. Life Events (Every 5 days)
        event_msg = None
        if self.day % 5 == 0:
            events = [
                ("A pipe burst in your kitchen!", -500, -0.5),
                ("You won a local lottery!", 200, 0.5),
                ("Your car needs a new battery.", -150, -0.2),
                ("Found $50 in an old jacket!", 50, 0.1),
                ("Health insurance premium due.", -300, -0.3)
            ]
            event_name, amount, event_reward = random.choice(events)
            self.balance += amount
            reward += event_reward
            event_msg = f"🌍 EVENT: {event_name} ({'+' if amount > 0 else ''}{amount}$)"
            
        # 2. Rent/Fixed Bill on Day 1
        if self.day == 1:
            self.balance -= 1200 # Fixed Rent
            
        # 3. Interest Rate (Investment Growth)
        self.balance *= 1.001 # 0.1% Daily Interest on balance
        
        # Increment day
        self.day += 1
        return self.state(), reward, done, event_msg

        # Check termination conditions
        if self.balance < 0:
            reward = -2.0
            done = True
        elif self.day > self.max_days:
            done = True

        return self.state(), reward, done
