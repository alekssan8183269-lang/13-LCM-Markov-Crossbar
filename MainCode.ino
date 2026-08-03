#include <math.h>

// ОПРЕДЕЛЕНИЕ НОЖЕК (ПИНОВ) ДЛЯ ЦИФРОВОГО ПОТЕНЦИОМЕТРА X9C103S
#define X9_INC  2  // Шаг изменения сопротивления (Pulse)
#define X9_UD   3  // Направление: 1 = вверх, 0 = вниз
#define X9_CS   4  // Выбор чипа (Чип активен при LOW)

// Ножка, куда прилетает суммарный аналоговый ток паники/ведер с ОУ
#define ANALOG_INPUT_PIN A0 

// Переменные марковского графа
float node_charges[26];    // Электрический заряд 26 вершин кубосферы
int active_pairs = 13;     // Изначально включены все 13 пар триггеров
int current_pot_position = 50; // Текущая позиция потенциометра (от 0 до 99)

void setup() {
  // Настраиваем ножки управления потенциометром на выход
  pinMode(X9_INC, OUTPUT);
  pinMode(X9_UD, OUTPUT);
  pinMode(X9_CS, OUTPUT);
  
  digitalWrite(X9_CS, HIGH); // Деактивируем потенциометр на старте
  
  // Обнуляем заряды когнитивных вершин графа
  for(int i = 0; i < 26; i++) {
    node_charges[i] = 0.0;
  }
  
  Serial.begin(9600); // Открываем порт для отладки
}

// ФУНКЦИЯ ДЛЯ ФИЗИЧЕСКОГО СДВИГА СОПРОТИВЛЕНИЯ ПОТЕНЦИОМЕТРА
void set_potentiometer(int target_position) {
  target_position = constrain(target_position, 0, 99);
  int steps = target_position - current_pot_position;
  
  if (steps == 0) return;
  
  digitalWrite(X9_CS, LOW); // Активируем чип X9C103S
  
  // Задаем направление сдвига Омов
  if (steps > 0) {
    digitalWrite(X9_UD, HIGH); // Вверх (Увеличиваем сопротивление)
  } else {
    digitalWrite(X9_UD, LOW);  // Вниз (Уменьшаем сопротивление)
    steps = -steps;
  }
  
  // Шпуляем импульсы шагов в цифровой потенциометр
  for (int i = 0; i < steps; i++) {
    digitalWrite(X9_INC, LOW);
    delayMicroseconds(2);
    digitalWrite(X9_INC, HIGH);
    delayMicroseconds(2);
  }
  
  digitalWrite(X9_CS, HIGH); // Сохраняем позицию в EEPROM и закрываем чип
  current_pot_position = target_position;
}

void loop() {
  // 1. Считываем сырой аналоговый ток паники с платы (от 0 до 1023)
  int raw_analog = analogRead(ANALOG_INPUT_PIN);
  float input_current = (raw_analog / 1023.0) * 10.0; // Переводим в условные вольты

  // 2. ДИНАМИЧЕСКОЕ "ДЫХАНИЕ" ОБЪЕМА ГРАФА
  // Измеряем силу шторма. Если ток высокий - активируем до 26 вершин, если покой - сжимаем до 6
  int active_nodes_limit = 6 + int(input_current * 2.0);
  active_nodes_limit = constrain(active_nodes_limit, 6, 26);

  // Закидываем энергию аналогового тока в случайную активную вершину графа (Марковский выбор)
  int lucky_node = random(0, active_nodes_limit);
  node_charges[lucky_node] += input_current * 0.4;

  // 3. МАРКОВСКАЯ ДИФФУЗИЯ (Перетекание мыслей по ребрам кубосферы)
  int active_windows = 0;
  
  for (int i = 0; i < active_nodes_limit; i++) {
    node_charges[i] *= 0.92; // Утечка ведер (забывание контекста)
    
    if (node_charges[i] > 3.5) {
      active_windows++; // Фиксируем вспыхнувшее окно ума
    }

    // Переливаем заряды между соседними вершинами
    for (int j = 0; j < active_nodes_limit; j++) {
      if (i != j) {
        // Геометрическое марковское перетекание: чем ближе вершины, тем легче течет ток
        float probability = 1.0 / (abs(i - j) + 1.0);
        if (node_charges[i] > 0.1) {
          float flow = node_charges[i] * probability * 0.05;
          node_charges[i] -= flow;
          node_charges[j] += flow;
        }
      }
    }
  }

  // 4. КВАНТОВЫЙ ВЫХОД НА ЦИФРОВОЙ ПОТЕНЦИОМЕТР
  // Матрица Маркова вычисляет финальную позицию для потенциометра
  // Чем больше окон ума горит от перегрузки, тем сильнее мы крутим сопротивление делителя ОУ!
  int target_pot_pos = 15 + (active_windows * 3);
  set_potentiometer(target_pot_pos);

  // Выводим телеметрию в порт для контроля
  Serial.print("Analog_In: "); Serial.print(input_current);
  Serial.print(" | Active_Nodes: "); Serial.print(active_nodes_limit);
  Serial.print(" | Windows_Blown: "); Serial.print(active_windows);
  Serial.print(" | Pot_Ohm_Pos: "); Serial.println(current_pot_position);

  delay(30); // Шаг квантования времени (30 миллисекунд, как в нашем Python-симуляторе)
}
