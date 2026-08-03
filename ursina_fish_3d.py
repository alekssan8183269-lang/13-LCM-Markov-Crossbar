from ursina import *
import random
import math

# Инициализация красивого 3D движка Ursina
app = Ursina(title="Аква-Бионика: 3D Симулятор Марковской Рыбы")
window.fps_counter.enabled = True
window.exit_button.enabled = False

# --- 3D ДЕКОРАЦИИ И ОКРУЖАЮЩАЯ СРЕДА (СИНЯЯ ЗЕРКАЛЬНАЯ ВОДА) ---
Sky(color=color.dark_gray)
camera.position = (0, 8, -18)
camera.rotation_x = 25

# Создаем синюю толщу пруда
pond_water = Entity(
    model='cube', 
    scale=(30, 0.1, 20), 
    position=(0, -0.05, 0), 
    color=color.Color(210, 0.9, 0.3, 0.4), # Полупрозрачная синяя вода
    alpha=0.5
)

# Создаем глянцевую зеркальную гладь на поверхности воды
water_surface = Entity(
    model='plane', 
    scale=(30, 1, 20), 
    position=(0, 0, 0), 
    color=color.Color(200, 0.8, 0.5, 0.2), 
    texture='white_cube' # Дает легкий эффект глянцевого отблеска
)

# --- АНАТОМИЯ БИОНИЧЕСКОЙ 3D-РЫБКИ ---
# Хребет рыбы состоит из 6 сегментов, соединенных цепью плавного следования
fish_segments = []
segment_scales = [1.2, 1.0, 0.8, 0.6, 0.4, 0.2] # От толстой головы к тонкому хвосту

for i in range(6):
    seg = Entity(
        model='sphere', 
        color=color.pink, 
        scale=(segment_scales[i], segment_scales[i]*0.6, segment_scales[i]),
        position=(-i * 0.8, 0, 0)
    )
    fish_segments.append(seg)

# Добавим рыбке красивые светящиеся кошачьи усы-вибриссы на голову
left_whisker = Entity(parent=fish_segments[0], model='cylinder', color=color.white, scale=(0.05, 1.2, 0.05), rotation_z=75, position=(0.5, 0, 0.4))
right_whisker = Entity(parent=fish_segments[0], model='cylinder', color=color.white, scale=(0.05, 1.2, 0.05), rotation_z=-75, position=(0.5, 0, -0.4))

# Физические координаты движения рыбы в пруду
fish_x, fish_z = 0.0, 0.0
fish_angle = 0.0
fish_y_velocity = 0.0  # Для прыжков вверх (сальто!)

# --- МОЗГ РЫБЫ: 13 НЕЧЕТНЫХ ПАР ТРИГГЕРОВ И МАРКОВСКИЕ ВСПЛЕСКИ ---
trigger_pairs = [random.uniform(-1.0, 1.0) for _ in range(13)]
discovered_skills_count = 0
discovered_patterns = set()

# --- ИНТЕРФЕЙС И КУЧА ПОЛЗУНКОВ ДЛЯ ИЗМЕНЕНИЯ ЦВЕТА И ФИЗИКИ ---
# Ursina позволяет делать крутые ползунки прямо на 3D экране
slider_chaos = Slider(text='Storm Sensors', min=0, max=10, default=3, y=0.45, x=-0.7, scale=0.8)
slider_pairs = Slider(text='Active Triggers', min=3, max=13, default=13, step=1, y=0.40, x=-0.7, scale=0.8)

# Ползунки настройки цвета неоновой рыбки (RGB каналы)
slider_r = Slider(text='Fish Color R', min=0, max=1, default=0.9, y=0.32, x=-0.7, color=color.red, scale=0.8)
slider_g = Slider(text='Fish Color G', min=0, max=1, default=0.2, y=0.27, x=-0.7, color=color.green, scale=0.8)
slider_b = Slider(text='Fish Color B', min=0, max=1, default=0.6, y=0.22, x=-0.7, color=color.blue, scale=0.8)

# Текстовые логи эволюции прямо в 3D мире
lbl_time = Text(text="Time: 0.0s", position=(-0.8, -0.35), scale=1.1, color=color.white)
lbl_skills = Text(text="Skills Invented: 0", position=(-0.8, -0.40), scale=1.1, color=color.green)
lbl_status = Text(text="Status: Drift", position=(-0.8, -0.45), scale=1.2, color=color.yellow)

start_time = time.time()
wave_timer = 0.0

# --- ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ (КАЖДЫЙ КАДР ОБНОВЛЕНИЯ) ---
def update():
    global fish_x, fish_z, fish_angle, fish_y_velocity, trigger_pairs, discovered_skills_count, wave_timer
    
    elapsed = time.time() - start_time
    lbl_time.text = f"Time: {elapsed:.1f}s"

    # Считываем ползунки
    pond_chaos = slider_chaos.value
    active_pairs = int(slider_pairs.value)
    
    # Плавная интерактивная смена цвета рыбки ползунками!
    current_fish_color = color.rgb(slider_r.value, slider_g.value, slider_b.value)
    for seg in fish_segments:
        seg.color = current_fish_color

    # Имитируем узкие маски 7 датчиков хаоса в воде
    sensor_inputs = [0.0] * 7
    if pond_chaos > 0:
        for s in range(6):
            sensor_inputs[s] = random.uniform(-pond_chaos, pond_chaos)

    # 1. ОБСЧЁТ 13 НЕЧЕТНЫХ ТРИГГЕРОВ НА ЗАДНЕМ ПЛАНЕ
    dt = 0.1
    new_triggers = list(trigger_pairs)
    for i in range(active_pairs):
        next_idx = (i + 1) % active_pairs
        prev_idx = (i - 1) % active_pairs
        influence = sensor_inputs[i] if i < 6 else 0.0
        
        dv = (math.sin(trigger_pairs[prev_idx]) - trigger_pairs[i] * 0.4 + influence)
        new_triggers[i] += dv * dt
        new_triggers[i] = max(-5.0, min(5.0, new_triggers[i]))
    trigger_pairs = new_triggers

    # Вычисляем отпечаток ума (сколько окон вспыхнуло)
    active_windows = 0
    pattern_binary = ""
    for i in range(active_pairs):
        if abs(trigger_pairs[i]) > 1.2:
            pattern_binary += "1"
            active_windows += 1
        else:
            pattern_binary += "0"

    # Счетчик уникальных марковских алгоритмов
    if active_windows > 0 and "1" in pattern_binary and pattern_binary not in discovered_patterns:
        discovered_patterns.add(pattern_binary)
        discovered_skills_count = len(discovered_patterns)
        lbl_skills.text = f"Skills Invented: {discovered_skills_count}"

    # 2. ПЕРЕВОД МАТЕМАТИКИ ТОКОВ В ФИЗИКУ ТЕЛА РЫБЫ
    # Суммарный ток всех триггеров рождает хвостовую волну биения
    brain_total_output = sum(trigger_pairs[:active_pairs])
    
    wave_timer += time.dt * (5.0 + abs(brain_total_output) * 2.0)
    # Плавное виляние хвоста на основе триггерного баланса
    tail_wave = math.sin(wave_timer) * (0.2 + active_windows * 0.1)

    # Логика принятия решений (Эмерджентные режимы)
    if active_windows >= 9 and fish_segments[0].y <= 0.05:
        # ВСПЛЕСК РИККАТИ: Квантовое Сальто! Рыба прыгает вверх над водой!
        fish_y_velocity = 4.5
        lbl_status.text = "STATUS: QUANTUM FLIP (SALTO)!"
        lbl_status.color = color.red
    elif active_windows >= 4:
        lbl_status.text = "STATUS: ACTIVE HUNTING"
        lbl_status.color = color.orange
    else:
        lbl_status.text = "STATUS: SMOOTH DRIFT"
        lbl_status.color = color.yellow

    # Гравитация и подъем над водой (Прыжки)
    fish_segments[0].y += fish_y_velocity * time.dt
    if fish_segments[0].y > 0:
        fish_y_velocity -= 9.8 * time.dt # Сила тяжести тянет рыбку обратно в пруд
    else:
        fish_segments[0].y = 0
        fish_y_velocity = 0

    # Движение головы по плоскости зеркала воды пруда
    # Если рыба летит в сальто, она движется по инерции вперед
    speed = 1.5 + (active_windows * 0.5) if fish_segments[0].y == 0 else 4.0
    fish_angle += tail_wave * time.dt * 15.0
    
    fish_x += math.cos(math.radians(fish_angle)) * speed * time.dt
    fish_z += math.sin(math.radians(fish_angle)) * speed * time.dt

    # Возврат в пруд при уплывании за границы
    if abs(fish_x) > 13: fish_x = -fish_x
    if abs(fish_z) > 8: fish_z = -fish_z

    # Обновляем координаты головы рыбы
    fish_segments[0].x = fish_x
    fish_segments[0].z = fish_z
    fish_segments[0].rotation_y = -fish_angle + 90

    # 3. АЛГОРИТМ ИНВЕРСНОЙ КИНЕМАТИКИ ХРЕБТА (Сегменты плавно текут за головой)
    for i in range(1, 6):
        prev_seg = fish_segments[i-1]
        curr_seg = fish_segments[i]
        
        # Считаем вектор до предыдущего звена
        dir_vector = curr_seg.position - prev_seg.position
        # Удерживаем строгое биологическое расстояние между позвонками в воде
        # dir_vector = dir_vector.normalize() * 0.75
        # dir_vector = normalize(dir_vector) * 0.75
        # dir_vector = dir_vector.normalized * 0.75
        
        if dir_vector.length() > 0:
            dir_vector = (dir_vector / dir_vector.length()) * 0.75
        
        # Плавное перетекание координаты (вязкость воды пруда)
        target_pos = prev_seg.position + dir_vector
        curr_seg.position = lerp(curr_seg.position, target_pos, time.dt * 20.0)
        
        # Передаем угловую волну биения триггеров по хребту назад к хвосту
        curr_seg.rotation_y = lerp(curr_seg.rotation_y, prev_seg.rotation_y + (tail_wave * 12.0), time.dt * 15.0)
        # Если голова в воздухе (сальто), хвост летит по параболе за ней
        if fish_segments[0].y > 0:
            curr_seg.y = lerp(curr_seg.y, prev_seg.y - 0.1, time.dt * 25.0)
        else:
            curr_seg.y = 0

# Запуск нашей великолепной 3D био-вселенной
app.run()
