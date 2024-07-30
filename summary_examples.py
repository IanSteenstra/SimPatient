import matplotlib.pyplot as plt
import numpy as np
import random

# Sample Data (Replace with your actual scores)
cultivating_change_talk_score = 3.5
softening_sustain_talk_score = 2.8
partnership_score = 4.2
empathy_score = 3.9

cr_count = 12
sr_count = 8
q_count = 20
gi_count = 5 
# ... (Add counts for other behaviors)

percent_cr = 30 # Example percentage
reflect_question_ratio = 2.5 # Example ratio

total_mi_adherent = 75
total_mi_non_adherent = 25 

# --- Radar Chart ---
categories = ['Cultivating\nChange Talk', 'Softening\nSustain Talk', 'Partnership', 'Empathy']
scores = [cultivating_change_talk_score, softening_sustain_talk_score, partnership_score, empathy_score]

N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
scores += scores[:1] # Close the shape
angles += angles[:1]

fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111, polar=True)
plt.xticks(angles[:-1], categories, color='grey', size=12)
ax.set_rlabel_position(0)
plt.yticks([1, 2, 3, 4, 5], ["1", "2", "3", "4", "5"], color="gray", size=10)
plt.ylim(0,5)

ax.plot(angles, scores, linewidth=1, linestyle='solid')
ax.fill(angles, scores, color='skyblue', alpha=0.4)
plt.title('MI Global Scores', size=14)
plt.show()

# --- Bar Chart ---
behavior_codes = ["GI", "Persuade", "Persuade with", "Q", "SR", "CR", "AF", "Seek", "Emphasize", "Confront"] 
counts = [gi_count, 3, 8, q_count, sr_count, cr_count, 10, 6, 20, 0]

plt.figure(figsize=(8, 4))
plt.bar(behavior_codes, counts, color='lightcoral')
plt.xlabel('MI Behavior Codes')
plt.ylabel('Frequency')
plt.title('Frequency of MI Behaviors')
plt.show()

# --- Pie Chart ---
labels = ['MI Adherent', 'MI Non-Adherent']
sizes = [total_mi_adherent, total_mi_non_adherent]
colors = ['lightgreen', 'lightcoral']
plt.figure(figsize=(5, 5))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
plt.axis('equal')  # Equal aspect ratio ensures a circle
plt.title('Adherence to MI Principles')
plt.show()