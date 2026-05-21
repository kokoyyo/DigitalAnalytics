import matplotlib.pyplot as plt
import numpy as np

# Ваши данные
names = ['Бариста', 'Кладовщик', 'Старший бариста', 'Уборщик', 'Управляющий']
position_ids = [3, 4, 2, 5, 1]
sales = [4347, 5699, 2990, 4467, 2823]

# Сортировка по убыванию продаж
sorted_data = sorted(zip(names, position_ids, sales), key=lambda x: x[2], reverse=True)
names, position_ids, sales = zip(*sorted_data)

# Позиции для столбцов
xpos = np.arange(len(names))  # 0, 1, 2, 3, 4
ypos = np.zeros(len(names))   # все на одной линии
zpos = np.zeros(len(names))   # старт с 0

# Ширина столбцов
dx = 0.6
dy = 0.6
dz = sales

# Цвета (от темного к светлому)
colors = plt.cm.Blues(np.array(sales) / max(sales))

# --- Построение 3D гистограммы ---
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True, alpha=0.9)

# Настройка подписей
ax.set_xticks(xpos)
ax.set_xticklabels(names, rotation=30, ha='right', fontsize=11)
ax.set_xlabel('Должности', fontsize=12, labelpad=10)
ax.set_ylabel('')
ax.set_zlabel('Количество продаж', fontsize=12, labelpad=10)
ax.set_title('Продажи по должностям (3D гистограмма)', fontsize=14, fontweight='bold')

# Добавление значений на столбцах
for i, (x, y, z) in enumerate(zip(xpos, ypos, sales)):
    ax.text(x, y, z + 150, f'{int(z)}', ha='center', va='bottom', fontsize=10)

# Убираем ось Y (она не нужна)
ax.set_yticklabels([])
ax.set_yticks([])

plt.tight_layout()
plt.show()