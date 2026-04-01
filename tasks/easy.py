from env.expense_env import ExpenseEnv

def evaluate_easy(agent_func, episodes=1):
    """
    Easy Task: Goal is to save for at least 7 days.
    Score = (Number of Successful Days / 7)
    Max score = 1.0
    """
    env = ExpenseEnv()
    total_score = 0

    for _ in range(episodes):
        state = env.reset()
        done = False
        save_count = 0
        target_days = 7

        while not done and env.day <= target_days:
            # Agent decides action based on state
            action = agent_func(state)
            state, reward, done = env.step(action)
            if action == 1:  # Saved
                save_count += 1

        total_score += min(1.0, save_count / target_days)

    return total_score / episodes

EASY_TASKS = {"save_7_days": evaluate_easy}
