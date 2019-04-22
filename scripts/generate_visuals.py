import matplotlib.pyplot as plt
import csv


def generate_sample():

    x = [1, 2, 3, 4, 5, 6, 7, 8]
    y = [1, 2, 4, 8, 16, 32, 64, 48]

    """
    with open('example.txt','r') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            x.append(int(row[0]))
            y.append(int(row[1]))
    """

    plt.plot(x,y, label='sample graph')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Interesting Graph\nCheck it out')
    plt.legend()
    plt.show()

def generate_exchange_sort_graphs():
    '''name,pipeline_enabled,input_size,cycles,correct'''

    data = dict()

    with open("scripts/results/exchange_sort_Apr19_v3.txt") as f:
        rows = csv.reader(f, delimiter=',')
        next(rows) # skip header

        for row in rows:

            name = row[0].replace('_no_pipelining','')
            if name not in data:
                data[name] = {'pipelined': {'x':[], 'y':[]}, 'not': {'x':[], 'y':[]}}

            if 'T' in row[1]:
                data[name]['pipelined']['x'].append(int(row[2]))
                data[name]['pipelined']['y'].append(int(row[3]))
            else:
                data[name]['not']['x'].append(int(row[2]))
                data[name]['not']['y'].append(int(row[3]))

    # Graph per config
    for name in data.keys():
        x = data[name]['pipelined']['x']
        y = data[name]['pipelined']['y']
        if len(y) != 0:
            plt.plot(x, y)

        x = data[name]['not']['x']
        y = data[name]['not']['y']
        if len(y) != 0:
            plt.plot(x, y)


        plt.legend(['pipelined', 'not'], loc='upper left')
        plt.xlabel('input size')
        plt.ylabel('# Cycles')
        plt.title(name)
        plt.savefig('scripts/results/{}.png'.format(name))
        print('scripts/results/{}.png saved'.format(name))
        plt.clf()

    # Graph combined
    i = 0
    colors = ['C0','C1','C2', 'C3']
    legend = []
    for name in data.keys():
        x = data[name]['pipelined']['x']
        y = data[name]['pipelined']['y']
        print(name, y)
        if len(y) != 0:
            plt.plot(x, y, linestyle='-', color=colors[i])
            legend.append(name)

        x = data[name]['not']['x']
        y = data[name]['not']['y']
        print(name, y)
        if len(y) != 0:
            plt.plot(x, y, linestyle=':', color=colors[i])
            legend.append(name + ' (np)')

        i += 1

    plt.legend(legend, loc='upper left')
    plt.xlabel('input size (n = 2**x)')
    plt.ylabel('# Cycles')
    plt.title('Exchange Sort Performance')
    plt.savefig('scripts/results/exchange_sort.png')
    print('scripts/results/exchange_sort.png')


if __name__ == "__main__":
    generate_exchange_sort_graphs()
