import pandas as pd
import matplotlib.pyplot as plt


def plot_heating_report(csv_file):
    try:
        # 1. Загружаем данные
        df = pd.read_csv(csv_file)

        # 2. ОЧИСТКА ДАННЫХ (вставляем сюда)
        df['t_vhod'] = pd.to_numeric(df['t_vhod'], errors='coerce')
        df['t_vihod'] = pd.to_numeric(df['t_vihod'], errors='coerce')
        df = df.dropna(subset=['t_vhod', 't_vihod'])

        # Преобразуем время
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['delta'] = df['t_vihod'] - df['t_vhod']

        # 3. Строим графики
        plt.figure(figsize=(12, 6))
        # ... тут идет остальной код отрисовки ...

        # Верхний график: Температуры
        plt.subplot(2, 1, 1)
        plt.plot(df['timestamp'], df['t_vhod'], label='Вход (обратка)', color='blue')
        plt.plot(df['timestamp'], df['t_vihod'], label='Выход котла', color='red')
        plt.title('Мониторинг температур котла')
        plt.ylabel('Градусы C')
        plt.legend()
        plt.grid(True)

        # Нижний график: Дельта (нагрев)
        plt.subplot(2, 1, 2)
        plt.fill_between(df['timestamp'], df['delta'], color='orange', alpha=0.3, label='Нагрев (ΔT)')
        plt.plot(df['timestamp'], df['delta'], color='orange')
        plt.title('Эффективность работы (Разница температур)')
        plt.ylabel('Дельта C')
        plt.xlabel('Время')
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.savefig('heating_report.png')  # Сохраняем график в файл
        plt.show()

    except Exception as e:
        print(f"Ошибка при анализе: {e}")


if __name__ == "__main__":
    plot_heating_report('heating_log.csv')