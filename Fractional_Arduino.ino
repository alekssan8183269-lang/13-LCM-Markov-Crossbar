#define NUM_NODES 26
#define MEMORY_WINDOW 6

// Коэффициенты Грюнвальда-Летникова для альфа = 0.75 (рассчитаны заранее для экономии ОЗУ)
const float fracWeights[MEMORY_WINDOW] = {1.0000, -0.7500, -0.0938, -0.0391, -0.0220, -0.0143};

float stateHistory[MEMORY_WINDOW][NUM_NODES];
int historyIndex = 0;
bool isHistoryFull = false;

void setup() {
  Serial.begin(115200);
  // Инициализация портов для мультиплексоров CD4051 и потенциометров X9C103S
  for(int i=0; i<MEMORY_WINDOW; i++) {
    for(int j=0; j<NUM_NODES; j++) stateHistory[i][j] = 0.0;
  }
}

void loop() {
  float currentSensors[NUM_NODES];
  
  // 1. Опрашиваем твои копеечные компоненты и усы рыбки
  for(int i=0; i<NUM_NODES; i++) {
    currentSensors[i] = analogRead(A0) / 1023.0; // Пример чтения аналогового тока Кирхгофа
  }

  // 2. Записываем в кольцевой буфер памяти атомов решетки
  for(int i=0; i<NUM_NODES; i++) {
    stateHistory[historyIndex][i] = currentSensors[i];
  }

  // 3. Считаем дробный шаг «в железе» (in-materio)
  float fractionalGraphUpdate[NUM_NODES];
  
  for(int node = 0; node < NUM_NODES; node++) {
    float sum = 0.0;
    for(int step = 0; step < MEMORY_WINDOW; step++) {
      // Идем назад во времени от текущего индекса
      int idx = historyIndex - step;
      if (idx < 0) idx += MEMORY_WINDOW;
      
      sum += fracWeights[step] * stateHistory[idx][node];
    }
    fractionalGraphUpdate[node] = sum;
  }

  // 4. Двигаем индекс буфера
  historyIndex++;
  if(historyIndex >= MEMORY_WINDOW) historyIndex = 0;

  // 5. Выдаем дробный синаптический ток на цифровой потенциометр X9C103S
  // Здесь твой «дышащий» граф физически меняет геометрию кубосферы!
  analogWrite(9, constrain(fractionalGraphUpdate[0] * 255, 0, 255)); 

  delay(20); // 10-секундный перекур процессора в масштабе миллисекунд :)
}
