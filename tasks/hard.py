from env.expense_env import ExpenseEnv

def evaluate_hard(agent_func, episodes=1):
    """
    Hard Task: Survived for 30 days and maintained a healthy balance.
    Score = (Day reached / 30) * (Normalized Balance Score)
    Balance penalty if balance is consistently low.
    Max score = 1.0
    """
    env = ExpenseEnv()
    total_score = 0

    for _ in range(episodes):
        state = env.reset()
        done = False
        target_days = 30
        
        while not done:
            # Dynamic decision based on balance (state['balance'])
            action = agent_func(state)
            state, reward, done = env.step(action)
            
        final_balance = state['balance']
        day_reached = state['day'] - 1

        day_factor = min(1.0, day_reached / target_days)
        balance_factor = min(1.0, max(0.0, final_balance / 5000))

        episode_score = (day_factor * 0.7) + (balance_factor * 0.3)
        total_score += episode_score

    return total_score / episodes

HARD_TASKS = {"dynamic_management_30_days": evaluate_hard}
