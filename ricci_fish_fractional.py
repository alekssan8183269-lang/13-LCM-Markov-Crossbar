import numpy as np

class FractionalMemoryCore:
    """
    Дробный когнитивный демпфер для Рыбки Рикки.
    Реализует дискретный оператор Грюнвальда-Летникова порядка alpha.
    """
    def __init__(self, alpha=0.73, window_size=15, num_nodes=26):
        self.alpha = alpha          # Порядок дробной производной (индекс вязкости ума)
        self.window = window_size   # Глубина атомной памяти (окно замера)
        self.num_nodes = num_nodes  # Твои 26 когнитивных вершин
        
        # Хранилище предыстории состояний графа
        self.history = []
        
        # Заранее рассчитываем биномиальные коэффициенты, чтобы процессор не тупил
        self.weights = [1.0]
        for j in range(1, self.window):
            w = self.weights[-1] * (j - 1 - self.alpha) / j
            self.weights.append(w)
            
    def compute_fractional_step(self, current_state, lcm_chaos_vector):
        """
        Принимает текущие токи датчиков и вектор 13 LCM-осцилляторов.
        Возвращает дробно-сглаженный импульс для нейрогенеза графа.
        """
        # Добавляем текущее состояние с учетом хаоса от триггерных пар
        modified_state = current_state * (1.0 + 0.1 * lcm_chaos_vector)
        self.history.append(modified_state)
        
        if len(self.history) > self.window:
            self.history.pop(0)
            
        # Запуск дробного суммирования памяти (эффект вязкой среды)
        fractional_derivative = np.zeros(self.num_nodes)
        actual_len = len(self.history)
        
        for j in range(actual_len):
            # Идем с конца истории к началу
            hist_state = self.history[actual_len - 1 - j]
            fractional_derivative += self.weights[j] * hist_state
            
        return fractional_derivative

# Тестовый прогон для Ursina 3D контура
if __name__ == "__main__":
    # Симулируем 26 вершин ума рыбки
    dummy_nodes = np.random.rand(26)
    # 13 генераторов хаоса
    lcm_chaos = np.random.choice([-1, 1], size=13) 
    
    core = FractionalMemoryCore(alpha=0.73, window_size=10)
    fractional_impulse = core.compute_fractional_step(dummy_nodes, lcm_chaos[:26]) # маппинг
    print("🔥 Дробный импульс для 26 вершин успешно рассчитан:\n", fractional_impulse[:5])
