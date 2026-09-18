import matplotlib.pyplot as plt
import pandas as pd


def plot_heating_report(csv_file):
    try:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.strip()

        # Приведение колонок к числовому формату
        for col in ["t_vhod", "t_vihod", "t_outdoors"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["t_vhod", "t_vihod"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["delta"] = df["t_vihod"] - df["t_vhod"]

        plt.figure(figsize=(12, 7))

        # Верхний график: Температуры
        plt.subplot(2, 1, 1)
        plt.plot(
            df["timestamp"], df["t_vhod"], label="Вход (обратка)", color="blue"
        )
        plt.plot(
            df["timestamp"], df["t_vihod"], label="Выход котла", color="red"
        )

        # Отрисовка уличной температуры (если есть в CSV)
        if "t_outdoors" in df.columns:
            plt.plot(
                df["timestamp"],
                df["t_outdoors"],
                label="Улица",
                color="green",
                linestyle="--",
                linewidth=1.5,
            )

        plt.title("Мониторинг температур котла и улицы")
        plt.ylabel("Градусы C")
        plt.legend(loc="upper right")
        plt.grid(True)

        # Нижний график: Дельта (нагрев)
        plt.subplot(2, 1, 2)
        plt.fill_between(
            df["timestamp"],
            df["delta"],
            color="orange",
            alpha=0.3,
            label="Нагрев (ΔT)",
        )
        plt.plot(df["timestamp"], df["delta"], color="orange")
        plt.title("Эффективность работы (Разница температур ΔT)")
        plt.ylabel("Дельта C")
        plt.xlabel("Время")
        plt.legend(loc="upper right")
        plt.grid(True)

        plt.tight_layout()
        plt.savefig("heating_report.png")
        plt.show()

    except Exception as e:
        print(f"Ошибка при анализе: {e}")


if __name__ == "__main__":
    plot_heating_report("heating_log.csv")