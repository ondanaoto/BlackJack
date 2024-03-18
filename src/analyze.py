import matplotlib.pyplot as plt

import agents
import simulation


def show_distribution(iter=1000, sample=1000):
    data = []
    for _ in range(sample):
        data.append(play(iter))
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=30, alpha=0.7, color="blue")
    plt.title("Histogram of Basic Strategy Agent")
    plt.xlabel("mean reward")
    plt.ylabel("Frequency")

    # ヒストグラムの表示
    plt.grid(True)
    plt.show()


def play(iter=1000) -> float:
    total_reward = 0
    agent = agents.BasicStrategyAgent()
    for _ in range(iter):
        total_reward += simulation.simulate(agent)
    return total_reward / iter


def show_playing(iterate_num=1000):
    total_reward = 0
    total_reward_history = []
    agent = agents.BasicStrategyAgent()

    plt.ion()  # インタラクティブモードをオンにする
    _, ax = plt.subplots()
    (line,) = ax.plot(total_reward_history)

    for _ in range(iterate_num):
        total_reward += simulation.simulate(agent)
        total_reward_history.append(total_reward)

        line.set_xdata(range(len(total_reward_history)))  # 新しいX値を設定
        line.set_ydata(total_reward_history)  # 新しいY値を設定
        ax.relim()  # リミットを再計算
        ax.autoscale_view()  # スケールを自動調整

        plt.draw()  # プロットを更新
        plt.pause(0.01)  # グラフを表示し続ける

    plt.ioff()  # インタラクティブモードをオフにする
    plt.show()  # 最終的なプロットを表示


if __name__ == "__main__":
    show_distribution()
