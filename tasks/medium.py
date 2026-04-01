from env.expense_env import ExpenseEnv

def evaluate_medium(agent_func, episodes=1):
    """
    Medium Task: Avoid spending (no action=0) for 15 days.
    Score = (Number of Successful Days / 15)
    If spending action happens, score is reduced.
    Max score = 1.0
    """
    env = ExpenseEnv()
    total_score = 0

    for _ in range(episodes):
        state = env.reset()
        done = False
        non_spend_count = 0
        target_days = 15

        while not done and env.day <= target_days:
            # Agent decides action
            action = agent_func(state)
            state, reward, done = env.step(action)
            if action != 0:  # Avoid spending
                non_spend_count += 1
            else:
                break  # Fail on spend

        total_score += min(1.0, non_spend_count / target_days)

    return total_score / episodes

MEDIUM_TASKS = {"avoid_spending_15_days": evaluate_medium}
