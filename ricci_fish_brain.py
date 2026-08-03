import tkinter as tk
import math
import random

class RicciFishBrainSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Мозг Водной Рыбки: 13 Нечетных Пар Триггеров в Хаосе Пруда")
        self.root.geometry("1000x720")
        self.root.resizable(False, False)

        # 3D Камера для графа кубосферы
        self.angle_x = 0.5
        self.angle_y = 0.6
        self.mx, self.my = 0, 0

        # Сила шторма/рандома в пруду (управляется ползунком)
        self.pond_chaos = 2.0

        # --- МОДЕЛЬ 13 НЕЧЕТНЫХ ПЕРЕКРЕСТНЫХ ТРИГГЕРНЫХ ПАР ---
        # Каждый триггер имеет два полярных состояния (Плюс и Минус). Всего 26 состояний!
        # Храним текущие аналоговые напряжения на триггерах (от -5В до +5В)
        self.trigger_pairs = [random.uniform(-1.0, 1.0) for _ in range(13)]
        self.trigger_history = [[] for _ in range(13)] # Для осциллографа

        # Геометрия дышащей кубосферы Маркова (26 вершин)
        self.nodes_geometry = self.generate_cubosphere_geometry()
        self.node_charges = [0.0] * 26

        self.create_widgets()
        self.update_simulation()

    def generate_cubosphere_geometry(self):
        # Распределяет 26 когнитивных модулей по вершинам, граням и ребрам 3D-фигуры
        nodes = []
        labels = [
            "Глаз:Блики", "Усы:Волна Л", "Усы:Волна П", "Кворум Стаи", "Радио КВ", "Ток Воды",
            "Паника", "Агрессия", "Любопытство", "Анабиоз", "Сон", "Охота", "Исследование", "Шок",
            "Мост1", "Мост2", "Мост3", "Мост4", "Мост5", "Мост6", "Мост7", "Мост8", "Мост9", "Мост10", "Мост11", "Мост12"
        ]
        # Математическая сетка кубосферы
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
        # Панель управления сверху
        control_panel = tk.Frame(self.root, bg="#130cb7", padx=10, pady=10)
        control_panel.pack(side=tk.TOP, fill=tk.X)

        tk.Label(control_panel, text="ШТОРМ В ПРУДУ (Рандом со всех датчиков):", fg="white", bg="#130cb7", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
        self.slider_chaos = tk.Scale(control_panel, from_=0.0, to=10.0, resolution=0.1, orient=tk.HORIZONTAL, bg="#5252dd", fg="white", width=12, length=200)
        self.slider_chaos.set(3.0)
        self.slider_chaos.pack(side=tk.LEFT, padx=5)

        tk.Label(control_panel, text="← КРУТИ МЫШКОЙ 3D МОЗГ РЫБЫ НА ЭКРАНЕ!", fg="#f1c40f", bg="#130cb7", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=30)

        # Главный Холст (3D Граф)
        self.canvas = tk.Canvas(self.root, width=1000, height=400, bg="#050510", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.mouse_down)
        self.canvas.bind("<B1-Motion>", self.mouse_move)

        # Нижний приборный отсек: Многоканальный Осциллограф 13 Нечетных Пар
        self.dashboard = tk.Frame(self.root, bg="#0f1123", height=200, padx=5, pady=5)
        self.dashboard.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(self.dashboard, text="ЖИВОЙ ОСЦИЛЛОГРАФ ПОЛЯ: Колебания 13 нечетных триггерных пар (Взаимная фрустрация)", fg="#52de97", bg="#0f1123", font=("Arial", 9, "bold")).pack(anchor="w", padx=10)
        
        self.graph_canvas = tk.Canvas(self.dashboard, width=650, height=140, bg="#000000", highlightthickness=1, highlightbackground="#52de97")
        self.graph_canvas.pack(side=tk.LEFT, padx=10, pady=5)

        # Телеметрия эмерджентных состояний
        self.lbl_telemetry = tk.Label(self.dashboard, text="АНАЛОГОВЫЙ СТАТУС РЫБЫ:\n--", fg="white", bg="#0f1123", font=("Courier", 9, "bold"), justify=tk.LEFT)
        self.lbl_telemetry.pack(side=tk.LEFT, padx=20, fill=tk.Y)

    def mouse_down(self, event):
        self.mx, self.my = event.x, event.y

    def mouse_move(self, event):
        self.angle_y += (event.x - self.mx) * 0.01
        self.angle_x += (event.y - self.my) * 0.01
        self.mx, self.my = event.x, event.y

    def project_3d(self, x, y, z):
        # Матрица вращения камеры вокруг 3D-графа
        y1 = y * math.cos(self.angle_x) - z * math.sin(self.angle_x)
        z1 = y * math.sin(self.angle_x) + z * math.cos(self.angle_x)
        x2 = x * math.cos(self.angle_y) + z1 * math.sin(self.angle_y)
        z2 = -x * math.sin(self.angle_y) + z1 * math.cos(self.angle_y)
        factor = 380 / (3.8 + z2)
        return int(500 + x2 * factor), int(200 - y1 * factor), z2

    def update_simulation(self):
        self.pond_chaos = self.slider_chaos.get()

        # ----------------------------------------------------
        # 1. БОМБАРДИРОВКА СИСТЕМЫ РАНДОМОМ (Шторм в пруду)
        # ----------------------------------------------------
        # Имитируем 7 датчиков: случайные всплески волн воды бьют по усам и мемристорам
        random_sensors_input = [random.uniform(-self.pond_chaos, self.pond_chaos) for _ in range(7)]

        # ----------------------------------------------------
        # 2. МАТЕМАТИКА 13 НЕЧЕТНЫХ ПАР С КАТУШКОЙ (Кольцевой хаос)
        # ----------------------------------------------------
        # Нечетное количество заставляет токи каскадно циклически опрокидывать соседей!
        dt = 0.1
        new_triggers = list(self.trigger_pairs)
        
        for i in range(13):
            # Взаимодействие по нечетному кольцу (каждый триггер давит на следующего в противофазе)
            next_idx = (i + 1) % 13
            prev_idx = (i - 1) % 13
            
            # Втекающий случайный ток от 7 датчиков
            sensor_influence = sum(random_sensors_input[k] * math.sin(i+k) for k in range(7)) * 0.1
            
            # Дифференциальное уравнение LCM-триггера с индуктивным сдвигом фазы
            # Квадратичный член мемристора (Риккати) + фрустрация кольца Максвелла
            dv = (math.sin(self.trigger_pairs[prev_idx]) - self.trigger_pairs[i] * 0.4 + sensor_influence)
            new_triggers[i] += dv * dt
            
            # Ограничиваем физический порог питания схемы (+/- 5 Вольт)
            new_triggers[i] = max(-5.0, min(5.0, new_triggers[i]))

            # Записываем историю для осциллографа
            self.trigger_history[i].append(new_triggers[i])
            if len(self.trigger_history[i]) > 650:
                self.trigger_history[i].pop(0)

        self.trigger_pairs = new_triggers

        # ----------------------------------------------------
        # 3. СТЫКОВКА С 26 ВЕРШИНАМИ ДЫШАЩЕГО ГРАФА КУБОСФЕРЫ
        # ----------------------------------------------------
        # 13 триггерных пар имеют ровно 26 полярных выходов (Плюс и Минус)!
        # Переливаем эти токи напрямую в электрический заряд 26 когнитивных модулей графа
        for i in range(13):
            val = self.trigger_pairs[i]
            if val >= 0:
                self.node_charges[i*2] = val * 15.0         # Четные вершины — Плюс-состояния
                self.node_charges[i*2+1] = 0.0
            else:
                self.node_charges[i*2] = 0.0
                self.node_charges[i*2+1] = abs(val) * 15.0  # Нечетные вершины — Минус-состояния

        # Считаем количество ОДНОВРЕМЕННО скомбинированных датчиков и триггеров
        active_states_count = sum(1 for c in self.node_charges if c > 12.0)

        # Телеметрия эмерджентного поведения рыбы
        status_text = "РЕЖИМ ЖИЗНИ РЫБКИ:\n"
        if active_states_count <= 2:
            status_text += " Равномерное скольжение\n по воде (Покой)."
        elif active_states_count <= 5:
            status_text += f" Гибридный режим:\n Охота + Рыскание усами\n (Скомбинировано {active_states_count} окон!)"
        else:
            status_text += f" ⚠️ КВАНТОВЫЙ ШТОРМ МЫСЛЕЙ!\n Изобретён новый алгоритм\n из {active_states_count} датчиков одновременно!\n Рыбка делает сальто."

        self.lbl_telemetry.config(text=f"{status_text}\n\nПотребление LCM: {2.5 * active_states_count:.1f} мВт")

        # Отрисовка кадров
        self.draw_3d_graph()
        self.draw_oscilloscope()

        self.root.after(30, self.update_simulation)

    def draw_3d_graph(self):
        self.canvas.delete("all")
        self.canvas.create_text(500, 25, text="ДЫШАЩИЙ МАРКОВСКИЙ МОЗГ РЫБЫ (26 ВЕРШИН ПУЛЬСИРУЮТ ОТ 13 ПАР ТРИГГЕРОВ)", fill="#52de97", font=("Arial", 11, "bold"))

        # Проецируем вершины кубосферы в 2D с учетом динамического дыхания объема
        projected = {}
        for idx in range(26):
            x, y, z, label = self.nodes_geometry[idx]
            # Вершина физически раздувается от полярного тока своего триггера!
            scale = 130.0 + (self.node_charges[idx] * 2.5)
            sx, sy, depth = self.project_3d(x * scale, y * scale, z * scale)
            projected[idx] = (sx, sy, depth, label)

        # Рисуем связи (ребра графа)
        for i in range(26):
            for j in range(26):
                if i < j:
                    # Связываем геометрически близкие модули ума
                    dx = self.nodes_geometry[i][0] - self.nodes_geometry[j][0]
                    dy = self.nodes_geometry[i][1] - self.nodes_geometry[j][1]
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist < 0.95 and (self.node_charges[i] > 1.0 or self.node_charges[j] > 1.0):
                        sx1, sy1, _, _ = projected[i]
                        sx2, sy2, _, _ = projected[j]
                        
                        # Цвет связей показывает, какие марковские каналы сейчас горят от рандома пруда
                        color = "#ff7675" if (self.node_charges[i] > 25.0) else "#3c40c6" if self.node_charges[i] > 5.0 else "#1e272e"
                        self.canvas.create_line(sx1, sy1, sx2, sy2, fill=color, width=1)
                        
        # Рисуем сами вершины-модули ума
        nodes_render_list = [(projected[idx], idx) for idx in range(26)]
        nodes_render_list.sort(key=lambda x: x[0][2], reverse=True)
        # Сортировка Painter's
        for (sx, sy, _, label), idx in nodes_render_list:
            charge = self.node_charges[idx]
            r = max(4, int(5 + charge * 0.4))
            if r > 20: r = 25
            
            # Живые вершины горят неоновым цветом от лавины Риккати
            fill_color = "#ff3f34" if charge > 30.0 else "#05c46b" if charge > 5.0 else "#2c3e50"
            self.canvas.create_oval(sx-r, sy-r, sx+r, sy+r, fill=fill_color, outline="white", width=1)
            if charge > 8.0:
                self.canvas.create_text(sx, sy-r-8, text=label, fill="white", font=("Arial", 8, "bold"))

    def draw_oscilloscope(self):
        self.graph_canvas.delete("all")
        # Рисуем центральную нулевую линию Вольт
        self.graph_canvas.create_line(0, 70, 650, 70, fill="#222", dash=(2,2))
        # Отрисовываем кривые колебаний для всех 13 триггерных пар на одном экране!
        colors = ["#ff5252", "#34de97", "#3498db", "#f1c40f", "#9b59b6", "#e67e22", "#1abc9c", "#ff7675", "#74b9ff", "#a29bfe", "#ffeaa7", "#55efc4", "#fab1a0"]
        for i in range(13):
            history = self.trigger_history[i]
            if len(history) > 1:
                points = []
                for x_coord, val in enumerate(history):
                    # Масштабируем напряжение от -5В до +5В в 140 пикселей высоты холста
                    y_coord = 70 - int(val * 13)
                    points.append((x_coord, y_coord))
                self.graph_canvas.create_line(points, fill=colors[i], width=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = RicciFishBrainSimulator(root)
    root.mainloop()