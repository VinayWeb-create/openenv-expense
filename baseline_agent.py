import random
from env.expense_env import ExpenseEnv

def baseline_agent():
    """ Runs 5 episodes using a random action selection strategy. """
    env = ExpenseEnv()
    num_episodes = 5

    for episode in range(1, num_episodes + 1):
        state = env.reset()
        done = False
        total_reward = 0

        while not done:
            action = random.randint(0, 2)  # Random actions: 0, 1, or 2
            next_state, reward, done = env.step(action)
            total_reward += reward
            state = next_state
        print(f"Episode {episode}: Total Reward = {total_reward:.2f}")

if __name__ == "__main__":
    baseline_agent()
