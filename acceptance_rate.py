import matplotlib.pyplot as plt
import numpy as np

year_list = [2015, 2016, 2017, 2018, 2019, 2020]
submitted = [1383, 2403, 3240, 4856, 6743, 9454]
accepted = [403, 569, 678, 1011, 1428, 1900]

acceptance_rate = [j/i for i,j in zip(submitted, accepted)]
print(acceptance_rate)

opacity = 0.4
bar_width = 0.35

plt.xlabel('Year')
plt.ylabel('# of papers')

plt.xticks(range(len(submitted)+1000),('2015', '2016', '2017', '2018','2019', '2020'), rotation=30)
bar1 = plt.bar(np.arange(len(submitted))+ bar_width, submitted, bar_width, align='center', alpha=opacity, color='b', label='Submitted')
bar2 = plt.bar(range(len(submitted)), accepted, bar_width, align='center', alpha=opacity, color='r', label='Accepted')

# Add counts above the two bar graphs

for idx, rect in enumerate(bar1 + bar2):
    height = rect.get_height()

    plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(height), ha='center', va='bottom')


for idx, rect in enumerate(bar1 ):
    height = rect.get_height()
    plt.text(rect.get_x() + rect.get_width()/2., 0.35*height,
		        round(acceptance_rate[idx],3),
		        ha='center', va='bottom', rotation=90, color='red')
plt.legend()
plt.tight_layout()
plt.show()
