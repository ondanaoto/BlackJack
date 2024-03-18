from game import BlackJackEnv
from agents import BasicStrategyAgent

if __name__ == "__main__":
    env = BlackJackEnv()
    env.render()
    agent = BasicStrategyAgent()
    while True:
        action = agent.get_action(env.state)
        print(action)
        state, reward, done, _ = env.step(action)
        env.render()
        if done:
            print("done")
            print(f"dealer_deck:")
            for card in env.dealer_board.deck.cards:
                print(card.value)
            print(f"dealer_total: {env.dealer_board.deck.total}")
            print(f"reward: {reward}")
            break
