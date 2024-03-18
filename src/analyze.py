import matplotlib.pyplot as plt
import simulation
import agents

def analyze():
    total_reward = 0
    total_reward_history = []
    agent = agents.BasicStrategyAgent()

    plt.ion()  # インタラクティブモードをオンにする
    _, ax = plt.subplots()
    line, = ax.plot(total_reward_history)

    for _ in range(1000):
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
    analyze()




