from agent import agent
from environment import environment
import json
import random


class Game:
    def __init__(self, agent, env, num_episodes=50000, report_every=1000):
        self.agent = agent
        self.env = env
        self.num_episodes = num_episodes
        self.report_every = report_every
        self.wins = self.losses = self.draws = 0
        self.total_wins = self.total_losses = self.total_draws = 0
        self.history = []

    def play_episode(self):
        state = self.env.reset(agent_starts=random.choice([True, False]))
        done = False
        while not done:
            action = self.agent.choose_action(state)
            next_state, reward, done = self.env.step(action)
            self.agent.update(state, action, reward, next_state, done)
            state = next_state
        return self.env.get_result()

    def record(self, result):
        if result == "win":
            self.wins += 1
            self.total_wins += 1
        elif result == "loss":
            self.losses += 1
            self.total_losses += 1
        elif result == "draw":
            self.draws += 1
            self.total_draws += 1

    def report(self, episode):
        start = episode - self.report_every + 1
        win_pct = 100 * self.wins / self.report_every
        self.history.append({"start": start, "end": episode, "wins": self.wins, "losses": self.losses,
                             "draws": self.draws, "epsilon": round(self.agent.epsilon, 4)})
        print(f"Episodes {start:>6}-{episode:>6} | W {self.wins:>4}  L {self.losses:>4}  D {self.draws:>4}"
              f" | win {win_pct:5.1f}% | eps {self.agent.epsilon:.2f}")
        self.wins = self.losses = self.draws = 0

    def train(self, path="q_table.json"):
        for episode in range(1, self.num_episodes + 1):
            result = self.play_episode()
            self.record(result)
            self.agent.decay_epsilon()
            if episode % self.report_every == 0:
                self.report(episode)
        print(f"Total: W {self.total_wins:,}  L {self.total_losses:,}  D {self.total_draws:,}")
        meta = {
            "agent_mark": "X", "opponent_mark": "O", "empty": ".",
            "rewards": {"win": self.env.WIN_REWARD, "loss": self.env.LOSS_REWARD,
                        "draw": self.env.DRAW_REWARD, "move": self.env.MOVE_REWARD},
            "episodes": self.num_episodes, "alpha": self.agent.alpha, "gamma": self.agent.gamma,
        }
        self.agent.save(path, meta)
        with open("training_log.json", "w") as f:
            json.dump({"meta": meta, "blocks": self.history}, f, indent=1)


if __name__ == "__main__":
    a = agent(alpha=0.3, gamma=0.9, epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.9999)
    game = Game(a, environment(), num_episodes=50000, report_every=1000)
    game.train()
