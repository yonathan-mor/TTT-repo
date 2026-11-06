import json
import random


class agent:
    def __init__(self, alpha=0.3, gamma=0.9, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.9999):
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

    def legal_actions(self, state):
        return [i for i, c in enumerate(state) if c == "."]

    def get_q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0 if c == "." else None for c in state]
        return self.q_table[state]

    def best_action(self, state):
        q = self.get_q_values(state)
        legal = self.legal_actions(state)
        best = max(q[a] for a in legal)
        return random.choice([a for a in legal if q[a] == best])

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.legal_actions(state))
        return self.best_action(state)

    def update(self, state, action, reward, next_state, done):
        q = self.get_q_values(state)
        if done:
            target = reward
        else:
            next_q = self.get_q_values(next_state)
            best_next = max(next_q[a] for a in self.legal_actions(next_state))
            target = reward + self.gamma * best_next
        q[action] += self.alpha * (target - q[action])

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, path, meta=None):
        with open(path, "w") as f:
            json.dump({"meta": meta or {}, "q_table": self.q_table}, f)

    def load(self, path):
        with open(path) as f:
            data = json.load(f)
        self.q_table = data["q_table"]
        return data.get("meta", {})
