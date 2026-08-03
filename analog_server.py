import tkinter as tk
import math
import random

class AnalogServerSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Прототип Аналогового Мемристорного Сервера")
        self.root.geometry("980x680")
        self.root.resizable(False, False)

        # Состояние сервера
        self.is_running = False
        self.num_robots = 3     # Текущее число роботов, штурмующих сервер
        self.server_load = 0.0   # Общая токовая нагрузка на сервер
        self.output_signal = 0.0 # Выходной синхронизирующий импульс

        # Матрица мемристоров сервера (Кроссбар 4x4)
        # Хранит проводимость (G = 1/R) каждого мемристора в Сименсах
        self.crossbar_G = [[random.uniform(0.2, 0.8) for _ in range(4)] for _ in range(4)]
        self.row_currents = [0.0, 0.0, 0.0, 0.0] # Токи на горизонтальных шинах
        self.history_output = [] # Для графика осциллографа

        self.create_widgets()
        self.update_loop()

    def create_widgets(self):
        # Панель управления
        control_panel = tk.Frame(self.root, bg="#2c3e50", padx=10, pady=10)
        control_panel.pack(side=tk.TOP, fill=tk.X)

        self.btn_start = tk.Button(control_panel, text="СТАРТ СЕРВЕРА", command=self.toggle_server, bg="#2ecc71", fg="white", font=("Arial", 11, "bold"))
        self.btn_start.pack(side=tk.LEFT, padx=10)

        # Ползунок: Сколько роботов шлют радио-запросы на сервер
        tk.Label(control_panel, text="Роботы в комнате (Запросы к серверу):", fg="white", bg="#2c3e50", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
        self.slider_robots = tk.Scale(control_panel, from_=1, to=15, resolution=1, orient=tk.HORIZONTAL, bg="#34495e", fg="white", width=12, length=150)
        self.slider_robots.set(3)
        self.slider_robots.pack(side=tk.LEFT, padx=5)

        # Ползунок: Частота/Интенсивность паники роя (Входное напряжение)
        tk.Label(control_panel, text="Интенсивность волн роя (Входной Ток):", fg="white", bg="#2c3e50", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
        self.slider_voltage = tk.Scale(control_panel, from_=0.5, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, bg="#34495e", fg="white", width=12, length=150)
        self.slider_voltage.set(1.5)
        self.slider_voltage.pack(side=tk.LEFT, padx=5)

        # Главный Холст (Делим на Кроссбар и Инфо-панель)
        self.canvas = tk.Canvas(self.root, width=980, height=450, bg="#0b0c10", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Нижний осциллограф выходного сигнала сервера
        self.graph_frame = tk.Frame(self.root, bg="#1f2833", height=140, padx=5, pady=5)
        self.graph_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(self.graph_frame, text="ВЫХОДНОЙ СИНХРОНИЗИРУЮЩИЙ ИМПУЛЬС СЕРВЕРА (Аналоговый ответ рою)", fg="#66fcf1", bg="#1f2833", font=("Arial", 9, "bold")).pack(anchor="w", padx=10)
        self.graph_canvas = tk.Canvas(self.graph_frame, width=650, height=100, bg="#000000", highlightthickness=1, highlightbackground="#66fcf1")
        self.graph_canvas.pack(side=tk.LEFT, padx=10, pady=5)

        self.lbl_stats = tk.Label(self.graph_frame, text="ТЕЛЕМЕТРИЯ СЕРВЕРА:\n--", fg="white", bg="#1f2833", font=("Courier", 10, "bold"), justify=tk.LEFT)
        self.lbl_stats.pack(side=tk.LEFT, padx=20)

    def toggle_server(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_start.config(text="СТОП СЕРВЕР", bg="#f39c12")
        else:
            self.btn_start.config(text="СТАРТ СЕРВЕРА", bg="#2ecc71")

    def update_loop(self):
        if self.is_running:
            self.num_robots = self.slider_robots.get()
            input_v = self.slider_voltage.get()

            # --- МАТЕМАТИКА АНАЛОГОВОГО СЕРВЕРА (ЗАКОНЫ КИРХГОФА И ОМА) ---
            # Формируем входящие напряжения на вертикальных шинах (зависит от числа роботов)
            col_voltages = [0.0, 0.0, 0.0, 0.0]
            for col in range(4):
                # Нагрузка распределяется по шинам, имитируя каналы ДВ, СВ, КВ чувств
                if self.num_robots > col * 3:
                    col_voltages[col] = input_v * (1.0 + math.sin(col + random.uniform(0, 1)) * 0.1)

            # Обнуляем токи строк перед суммированием
            self.row_currents = [0.0, 0.0, 0.0, 0.0]

            # Считаем токи на пересечениях по закону Ома: I = V * G (Проводимость)
            # И суммируем их на горизонтальных шинах по первому закону Кирхгофа!
            for row in range(4):
                for col in range(4):
                    G = self.crossbar_G[row][col]
                    V = col_voltages[col]
                    current_at_node = V * G
                    self.row_currents[row] += current_at_node

                    # ФИЗИКА ОБУЧЕНИЯ МЕМРИСТОРОВ СЕРВЕРА (Уравнение Риккати)
                    # Если через узел течет сильный ток, проводимость мемристора плавно увеличивается (память сервера)
                    if current_at_node > 0.5:
                        self.crossbar_G[row][col] += (1.5 - G) * 0.01 # Лавинообразное открытие филамента
                    else:
                        # Плавное забывание/релаксация атомов, когда запросов нет
                        self.crossbar_G[row][col] -= (G - 0.2) * 0.003
                    
                    # Ограничиваем физические рамки проводимости материала
                    self.crossbar_G[row][col] = max(0.1, min(2.0, self.crossbar_G[row][col]))

            # Выходной ответ сервера — это сумма токов со всех горизонтальных линеек (Интеграл ОУ)
            self.output_signal = sum(self.row_currents)
            self.server_load = sum(sum(row) for row in self.crossbar_G) * input_v

            # Пишем историю для осциллографа
            self.history_output.append(self.output_signal)
            if len(self.history_output) > 650:
                self.history_output.pop(0)

            # Обновление логов
            self.lbl_stats.config(text=f"СЕРВЕРНАЯ СТОЙКА КРОССБАРА:\n"
                                       f"Потребление: {self.server_load:.2f} мВт\n"
                                       f"Выходной ток: {self.output_signal:.2f} мА\n"
                                       f"Статус: Сверхскоростной обсчёт")

        self.draw_server_scene()
        self.draw_graph()
        self.root.after(33, self.update_loop)

    def draw_server_scene(self):
        self.canvas.delete("all")
        
        # Отрисовка абстрактного роя червячков слева, шлющих радиоволны
        self.canvas.create_text(110, 40, text="🐛 РОЙ НА ПОЛУ", fill="#fff", font=("Arial", 11, "bold"))
        for i in range(min(8, self.num_robots)):
            y_pos = 90 + i * 40
            color = "#ff7675" if self.slider_voltage.get() > 3 else "#00cec9"
            self.canvas.create_oval(30, y_pos-10, 70, y_pos+10, fill=color, outline="white")
            # Лучи радиозапросов к серверу
            if self.is_running:
                self.canvas.create_line(70, y_pos, 220, 120 + (i%4)*60, fill="#6c5ce7", width=1, dash=(2,4))
        if self.num_robots > 8:
            self.canvas.create_text(50, 410, text=f"+ ещё {self.num_robots-8} шт.", fill="#bdc3c7", font=("Arial", 9, "italic"))

        # КОНСТРУКЦИЯ СЕРВЕРНОГО КРОССБАРА (Сетка шин)
        start_x, start_y = 300, 120
        step = 60

        self.canvas.create_text(400, 40, text="💾 АНАЛОГОВАЯ МЕМРИСТОРНАЯ МАТРИЦА СЕРВЕРА", fill="#66fcf1", font=("Arial", 12, "bold"))

        # Рисуем вертикальные шины (Входы Напряжения В)
        for col in range(4):
            x = start_x + col * step
            v_active = self.is_running and (self.num_robots > col * 3)
            line_color = "#00ff00" if v_active else "#333333"
            line_width = 3 if v_active else 1
            self.canvas.create_line(x, start_y-30, x, start_y + 3*step + 30, fill=line_color, width=line_width)
            self.canvas.create_text(x, start_y-45, text=f"Вход {col+1}", fill="#95afc0", font=("Arial", 8))

        # Рисуем горизонтальные шины (Выходы Тока I)
        for row in range(4):
            y = start_y + row * step
            i_active = self.is_running and self.row_currents[row] > 0.1
            line_color = "#66fcf1" if i_active else "#333333"
            line_width = 2 if i_active else 1
            self.canvas.create_line(start_x-30, y, start_x + 3*step + 60, y, fill=line_color, width=line_width)
            
            # Сумматоры на Операционных Усилителях (ОУ треугольники) на концах строк
            opamp_x = start_x + 3*step + 60
            self.canvas.create_polygon(opamp_x, y-12, opamp_x, y+12, opamp_x+20, y, fill="#1f2833", outline="#66fcf1")
            self.canvas.create_text(opamp_x-35, y-12, text=f"{self.row_currents[row]:.1f} мА", fill="#66fcf1", font=("Courier", 8, "bold"))

        # Рисуем МЕМРИСТОРЫ на пересечениях шин
        for row in range(4):
            for col in range(4):
                x = start_x + col * step
                y = start_y + row * step
                G = self.crossbar_G[row][col]

                # Размер и яркость мемристора показывают его текущую проводимость (память сервера!)
                r = int(4 + G * 5)
                if r > 16: r = 16
                
                # Если через узел течет сильный ток — мемристор раскаляется (краснеет) от джоулева тепла
                if self.is_running and (self.num_robots > col * 3) and self.slider_voltage.get() > 3.0:
                    node_color = "#ff7675" # Раскаленный мемрик
                else:
                    node_color = "#10ac84" if G > 0.8 else "#57606f" # Сытый или холодный

                self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=node_color, outline="white", width=1)
                
                # Выводим текущее аналоговое сопротивление узла в Омах (R = 1/G * 500 для масштаба графики)
                R_ohms = int(1.0 / G * 500)
                self.canvas.create_text(x, y+r+10, text=f"{R_ohms}Ω", fill="#bdc3c7", font=("Arial", 7))

                # Сборка общего выходного сигнала (Интегральный луч ОУ сервера обратно к рою)
                if self.is_running and self.output_signal > 0.5:
                    self.canvas.create_line(start_x + 3*step + 80, start_y+step, 800, 200, fill="#66fcf1", width=3)
                    self.canvas.create_oval(800-20, 200-20, 800+20, 200+20, fill="#111", outline="#66fcf1", width=2)
                    self.canvas.create_text(800, 200, text="📡\nИК", fill="#66fcf1", font=("Arial", 10, "bold"), justify=tk.CENTER)
                    # Обратный беспроводной ответ к рою червяков
                    self.canvas.create_line(800, 220, 70, 350, fill="#66fcf1", width=1, dash=(4,4))
                
    def draw_graph(self):
        self.graph_canvas.delete("all")
        if not self.history_output: return
        points = []
        for x_coord, val in enumerate(self.history_output):
            # Масштабируем выходной ток (от 0 до 40 мА) в 100 пикселей высоты
            y_coord = 100 - int(val * (100 / 40.0))
            if y_coord < 0: y_coord = 0
            points.append((x_coord, y_coord))
            
        if len(points) > 1:
            self.graph_canvas.create_line(points, fill="#66fcf1", width=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnalogServerSimulator(root)
    root.mainloop()