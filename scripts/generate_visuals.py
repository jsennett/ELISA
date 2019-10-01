import matplotlib.pyplot as plt
import csv


def generate_exchange_sort_graphs():
    '''name,pipeline_enabled,input_size,cycles,correct'''

    data = dict()

    with open("scripts/results/exchange_sort_Apr23.txt") as f:
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


        plt.legend(['Pipelined', 'Not'], loc='upper left')
        plt.xlabel('input size')
        plt.ylabel('# Cycles')
        plt.title(name)
        plt.savefig('scripts/results/{}_Apr23.png'.format(name))
        print('scripts/results/{}_Apr23.png saved'.format(name))
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
            legend.append(name + ' (No Pipelining)')

        i += 1

    plt.legend(legend, loc='upper left')
    plt.xlabel('input size')
    plt.ylabel('# Cycles')
    plt.title('Exchange Sort Performance')
    plt.savefig('scripts/results/exchange_sort_Apr23.png')
    print('scripts/results/exchange_sort_Apr23.png saved')


if __name__ == "__main__":
    generate_exchange_sort_graphs()
