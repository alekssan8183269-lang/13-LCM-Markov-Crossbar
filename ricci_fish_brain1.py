import tkinter as tk
import math
import random
import time

class RicciFishEvolutionSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Эволюционный стенд: Марковский мозг рыбы")
        self.root.geometry("1000x750")
        self.root.resizable(False, False)

        # 3D Камера
        self.angle_x = 0.5
        self.angle_y = 0.6
        self.mx, self.my = 0, 0

        # Время и Эволюция
        self.is_running = False
        self.start_time = None
        self.elapsed_time = 0.0
        self.discovered_algorithms = set() # Множество для уникальных комбинаций

        # Максимальная база геометрии кубосферы (26 вершин)
        self.nodes_geometry = self.generate_cubosphere_geometry()
        self.node_charges = [0.0] * 26
        self.markov_matrix = {}

        # Инициализация 13 пар триггеров
        self.trigger_pairs = [random.uniform(-1.0, 1.0) for _ in range(13)]
        self.trigger_history = [[] for _ in range(13)]

        self.create_widgets()
        self.update_simulation()

    def generate_cubosphere_geometry(self):
        nodes = []
        labels = [
            "Глаз:Блики", "Усы:Волна Л", "Усы:Волна П", "Кворум Стаи", "Радио КВ", "Ток Воды",
            "Паника", "Агрессия", "Любопытство", "Анабиоз", "Сон", "Охота", "Исследование", "Шок",
            "Мост1", "Мост2", "Мост3", "Мост4", "Мост5", "Мост6", "Мост7", "Мост8", "Мост9", "Мост10", "Мост11", "Мост12"
        ]
        for sign in [-1, 1]:
            nodes.append((sign, 0, 0, labels[len(nodes)]))
            nodes.append((0, sign, 0, labels[len(nodes)]))
            nodes.append((0, 0, sign, labels[len(nodes)]))
        for x in [-1, 1]:
            for y in [-1, 1]:
                for z in [-1, 1]:
                    nodes.append((x*0.6, y*0.6, z*0.6, labels[len(nodes)]))
        edges = [(1,1,0), (1,-1,0), (-1,1,0), (-1,-1,0), (1,0,1), (1,0,-1), (-1,0,1), (-1,0,-1), (0,1,1), (0,1,-1), (0,-1,1), (0,-1,-1)]
        for x, y, z in edges:
            if len(nodes) < 26:
                nodes.append((x*0.7, y*0.7, z*0.7, labels[len(nodes)]))
        return nodes

    def create_widgets(self):
        # Панель управления
        control_panel = tk.Frame(self.root, bg="#1e1e2f", padx=10, pady=10)
        control_panel.pack(side=tk.TOP, fill=tk.X)

        self.btn_start = tk.Button(control_panel, text="ПУСК", command=self.toggle_simulation, bg="#2ecc71", fg="white", font=("Arial", 11, "bold"))
        self.btn_start.pack(side=tk.LEFT, padx=10)

        btn_reset = tk.Button(control_panel, text="СБРОС", command=self.reset_simulation, bg="#e74c3c", fg="white", font=("Arial", 11, "bold"))
        btn_reset.pack(side=tk.LEFT, padx=10)

        # ПОЛЗУНОК 1: Шторм в пруду
        tk.Label(control_panel, text="Шторм датчиков:", fg="white", bg="#1e1e2f").pack(side=tk.LEFT, padx=5)
        self.slider_chaos = tk.Scale(control_panel, from_=0.0, to=10.0, resolution=0.1, orient=tk.HORIZONTAL, bg="#2d2d44", fg="white", width=10, length=120)
        self.slider_chaos.set(3.0)
        self.slider_chaos.pack(side=tk.LEFT, padx=5)

        # ПОЛЗУНОК 2: Динамическое количество пар триггеров (ВЕРШИН)
        tk.Label(control_panel, text="Активные пары триггеров (Ум):", fg="white", bg="#1e1e2f").pack(side=tk.LEFT, padx=5)
        self.slider_pairs = tk.Scale(control_panel, from_=3, to=13, resolution=1, orient=tk.HORIZONTAL, bg="#2d2d44", fg="white", width=10, length=120)
        self.slider_pairs.set(13) # По умолчанию максимум
        self.slider_pairs.pack(side=tk.LEFT, padx=5)

        # Главный 3D Холст
        self.canvas = tk.Canvas(self.root, width=1000, height=400, bg="#06060c", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.mouse_down)
        self.canvas.bind("<B1-Motion>", self.mouse_move)

        # Приборный отсек снизу
        self.dashboard = tk.Frame(self.root, bg="#111118", height=220, padx=8, pady=8)
        self.dashboard.pack(side=tk.BOTTOM, fill=tk.X)

        self.graph_canvas = tk.Canvas(self.dashboard, width=600, height=140, bg="#000000", highlightthickness=1, highlightbackground="#52de97")
        self.graph_canvas.pack(side=tk.LEFT, padx=10, pady=5)

        # Панель Эволюционной Телеметрии
        self.lbl_telemetry = tk.Label(self.dashboard, text="ЖИЗНЕННЫЙ ЦИКЛ:\n--", fg="white", bg="#111118", font=("Courier", 9, "bold"), justify=tk.LEFT)
        self.lbl_telemetry.pack(side=tk.LEFT, padx=20, fill=tk.Y)

    def toggle_simulation(self):
        self.is_running = not self.is_running
        if self.is_running:
            if self.start_time is None:
                self.start_time = time.time() - self.elapsed_time
            self.btn_start.config(text="ПАУЗА", bg="#f39c12")
        else:
            if self.start_time is not None:
                self.elapsed_time = time.time() - self.start_time
                self.start_time = None
            self.btn_start.config(text="ПУСК", bg="#2ecc71")

    def reset_simulation(self):
        self.is_running = False
        self.start_time = None
        self.elapsed_time = 0.0
        self.discovered_algorithms.clear()
        self.trigger_pairs = [random.uniform(-1.0, 1.0) for _ in range(13)]
        self.trigger_history = [[] for _ in range(13)]
        self.node_charges = [0.0] * 26
        self.btn_start.config(text="ПУСК", bg="#2ecc71")

    def mouse_down(self, event):
        self.mx, self.my = event.x, event.y

    def mouse_move(self, event):
        self.angle_y += (event.x - self.mx) * 0.01
        self.angle_x += (event.y - self.my) * 0.01
        self.mx, self.my = event.x, event.y

    def project_3d(self, x, y, z):
        y1 = y * math.cos(self.angle_x) - z * math.sin(self.angle_x)
        z1 = y * math.sin(self.angle_x) + z * math.cos(self.angle_x)
        x2 = x * math.cos(self.angle_y) + z1 * math.sin(self.angle_y)
        z2 = -x * math.sin(self.angle_y) + z1 * math.cos(self.angle_y)
        factor = 380 / (3.8 + z2)
        return int(500 + x2 * factor), int(200 - y1 * factor), z2

    def update_simulation(self):
        status_text = "АНАЛОГОВЫЙ МОНИТОР ЭВОЛЮЦИИ:\n Статус: Ожидание..."
        
        if self.is_running and self.start_time is not None:
            self.elapsed_time = time.time() - self.start_time
            pond_chaos = self.slider_chaos.get()
            active_pairs = self.slider_pairs.get() # Сколько пар триггеров включил пользователь
            active_nodes_limit = active_pairs * 2  # Количество активных вершин графа

            # ----------------------------------------------------
            # 1. СТРОГИЕ УЗКИЕ МАСКИ ДАТЧИКОВ (Исправление ошибки!)
            # ----------------------------------------------------
            # Теперь хаос пруда бьет строго по первым 6 сенсорным вершинам, а не по всему мозгу хаотично
            sensor_inputs = [0.0] * 26
            if pond_chaos > 0:
                for s_idx in range(6): # Только сенсоры: Блики, Волна Л, Волна П, Кворум, КВ, Ток
                    sensor_inputs[s_idx] = random.uniform(-pond_chaos, pond_chaos)

            # ----------------------------------------------------
            # 2. РАСЧЕТ ХАОСА НЕЧЕТНОГО КОЛЬЦА ТРИГГЕРОВ
            # ----------------------------------------------------
            dt = 0.1
            new_triggers = list(self.trigger_pairs)
            
            # Обсчитываем только то количество триггеров, которое задано ползунком
            for i in range(active_pairs):
                next_idx = (i + 1) % active_pairs
                prev_idx = (i - 1) % active_pairs
                
                # Ток идет строго через узкую маску датчика
                influence = sensor_inputs[i] if i < 6 else 0.0
                
                dv = (math.sin(self.trigger_pairs[prev_idx]) - self.trigger_pairs[i] * 0.4 + influence)
                new_triggers[i] += dv * dt
                new_triggers[i] = max(-5.0, min(5.0, new_triggers[i]))

                # Пишем историю
                self.trigger_history[i].append(new_triggers[i])
                if len(self.trigger_history[i]) > 600: self.trigger_history[i].pop(0)

            # Для выключенных триггеров плавно гасим историю в ноль
            for i in range(active_pairs, 13):
                self.trigger_history[i].clear()

            self.trigger_pairs = new_triggers

            # ----------------------------------------------------
            # 3. МАРКОВСКАЯ ДИФФУЗИЯ И СЧЕТЧИК АЛГОРИТМОВ
            # ----------------------------------------------------
            # Переносим полярные токи триггеров в вершины кубосферы
            for i in range(13):
                if i < active_pairs:
                    val = self.trigger_pairs[i]
                    if val >= 0:
                        self.node_charges[i*2] = val * 15.0
                        self.node_charges[i*2+1] = 0.0
                    else:
                        self.node_charges[i*2] = 0.0
                        self.node_charges[i*2+1] = abs(val) * 15.0
                else:
                    # Выключенные триггеры обнуляют свои вершины
                    self.node_charges[i*2] = 0.0
                    self.node_charges[i*2+1] = 0.0

            # Считаем текущий цифровой "отпечаток" (бинарный код активных окон)
            current_pattern_binary = ""
            active_windows = 0
            for idx in range(active_nodes_limit):
                if self.node_charges[idx] > 12.0:
                    current_pattern_binary += "1"
                    active_windows += 1
                else:
                    current_pattern_binary += "0"

            # ХАКЕРСКИЙ СЧЕТЧИК: Если такой комбинации еще не было в истории жизни — регистрируем её!
            if active_windows > 0 and "1" in current_pattern_binary:
                if current_pattern_binary not in self.discovered_algorithms:
                    self.discovered_algorithms.add(current_pattern_binary)
                    
                    # Собираем текстовое описание скомбинированных мыслей
                    compiled_skills = []
                    labels = [
                        "Блики", "Волна_Л", "Волна_П", "Кворум", "Радио", "Ток_Воды",
                        "Паника", "Агрессия", "Любопытство", "Анабиоз", "Сон", "Охота", "Исследование", "Шок"
                    ]
                    for char_idx, char in enumerate(current_pattern_binary):
                        if char == "1" and char_idx < len(labels):
                            compiled_skills.append(labels[char_idx])
                    
                    # Печатаем в черное окно консоли
                    print(f"[Алгоритм #{len(self.discovered_algorithms)}]: Поведение = {' + '.join(compiled_skills)}")
                    
            # Энергетическое перетекание по ребрам активной зоны графа
            for i in range(active_nodes_limit):
                self.node_charges[i] *= 0.93
                for j in range(active_nodes_limit):
                    if i != j:
                        dx = self.nodes_geometry[i][0] - self.nodes_geometry[j][0]
                        dy = self.nodes_geometry[i][1] - self.nodes_geometry[j][1]
                        dist = math.sqrt(dx**2 + dy**2)
                        prob = (1.0 / (dist + 0.1)) * (1.0 + pond_chaos * 0.04)
                        self.markov_matrix[(i, j)] = prob
                        if self.node_charges[i] > 0.1:
                            flow = self.node_charges[i] * prob * 0.02
                            self.node_charges[i] -= flow
                            self.node_charges[j] += flow

            # Обновление логов телеметрии
            # ВНИМАНИЕ: эти строки ниже ДОЛЖНЫ иметь ровно 8 пробелов от левого края!
            status_text = "АНАЛОГОВЫЙ МОНИТОР ЭВОЛЮЦИИ:\n"
            status_text += f" Время жизни: {self.elapsed_time:.1f} сек\n"
            status_text += f" Изобретено алгоритмов: {len(self.discovered_algorithms)}\n"
            status_text += f" Активных окон ума: {active_windows} / {active_nodes_limit}\n\n"
            
            if active_windows >= 9:
                status_text += " 🔥 КВАНТОВОЕ САЛЬТО В ПРУДУ!"
            elif active_windows >= 4:
                status_text += " 🏊 Режим: Активная охота"
            else:
                status_text += " 💤 Режим: Плавный дрейф"

            # --- ВАЖНЫЙ ВЫХОД ИЗ УСЛОВИЯ IF ---
            # Эти 4 строчки ниже должны иметь строго ЧЕТЫРЕ (4) пробела от левого края!
            # Они должны стоять на одном уровне с самым верхним "if self.is_running"                            
            self.lbl_telemetry.config(text=status_text)
            self.draw_3d_graph()
            self.draw_oscilloscope()
        self.root.after(30, self.update_simulation)

    def draw_3d_graph(self):
        self.canvas.delete("all")
        active_limit = self.slider_pairs.get() * 2
        self.canvas.create_text(500, 20, text=f"ЖИВАЯ КУБОСФЕРА: {active_limit} АКТИВНЫХ ВЕРШИН ИЗ 26", fill="#52de97", font=("Arial", 11, "bold"))
        projected = {}
        
        for idx in range(26):
            x, y, z, label = self.nodes_geometry[idx]
            scale = 130.0 + (self.node_charges[idx] * 2.5)
            sx, sy, depth = self.project_3d(x * scale, y * scale, z * scale)
            projected[idx] = (sx, sy, depth, label)
            
        # Рисуем ребра
        for i in range(active_limit):
            for j in range(active_limit):
                if i < j:
                    dx = self.nodes_geometry[i][0] - self.nodes_geometry[j][0]
                    dy = self.nodes_geometry[i][1] - self.nodes_geometry[j][1]
                    dist = math.sqrt(dx**2 + dy**2)
                    
                    if dist < 0.95 and (self.node_charges[i] > 1.0 or self.node_charges[j] > 1.0):
                        sx1, sy1, _, _ = projected[i]
                        sx2, sy2, _, _ = projected[j]
                        color = "#ff7675" if (self.node_charges[i] > 25.0) else "#3c40c6" if self.node_charges[i] > 5.0 else "#1c1c28"
                        self.canvas.create_line(sx1, sy1, sx2, sy2, fill=color, width=1)
                        
        # Рисуем вершины
        nodes_render_list = [(projected[idx], idx) for idx in range(26)]
        nodes_render_list.sort(key=lambda x: x[0][2], reverse=True)
        
        for (sx, sy, _, label), idx in nodes_render_list:
            if idx < active_limit:
                charge = self.node_charges[idx]
                r = max(4, int(5 + charge * 0.4))
                if r > 20:
                    r = 20
                fill_color = "#ff3f34" if charge > 30.0 else "#05c46b" if charge > 5.0 else "#2c3e50"
                self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=fill_color, outline="white", width=1)
                if charge > 8.0:
                    self.canvas.create_text(sx, sy - r - 8, text=label, fill="white", font=("Arial", 8, "bold"))
            else:
                # Отключенные вершины гаснут в темноте
                self.canvas.create_oval(sx - 2, sy - 2, sx + 2, sy + 2, fill="#111", outline="#222")

    def draw_oscilloscope(self):
        self.graph_canvas.delete("all")
        self.graph_canvas.create_line(0, 70, 600, 70, fill="#222", dash=(2, 2))
        colors = ["#ff5252", "#34de97", "#3498db", "#f1c40f", "#9b59b6", "#e67e22", "#1abc9c", "#ff7675", "#74b9ff", "#a29bfe", "#ffeaa7", "#55efc4", "#fab1a0"]
        active_pairs = self.slider_pairs.get()
        
        for i in range(13):
            if i < active_pairs:
                history = self.trigger_history[i]
                if len(history) > 1:
                    points = []
                    for x_coord, val in enumerate(history):
                        y_coord = 70 - int(val * 13)
                        points.append((x_coord, y_coord))
                    self.graph_canvas.create_line(points, fill=colors[i], width=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = RicciFishEvolutionSimulator(root)
    root.mainloop()