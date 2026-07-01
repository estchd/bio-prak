import matplotlib.pyplot as plt

def plot_accessibilities(sequence, footprints, looptypes, start, end, data, data_unmod, modifications):
    for u in footprints:
        fig, axs = plt.subplots(4, sharey = False, figsize = (20, 10))
        for k, v in data[u].items():
            axs[0].plot([i + start for i in range(len(sequence) + 1 - u + 1)], v, label = "{}, u={:d}".format(looptypes[k], u))
        axs[0].set_title("m6A")
        axs[0].set_xlabel("Sequence position")
        axs[0].set_ylabel("Probability to be unpaired")
        axs[0].legend()
        for k, v in data_unmod[u].items():
            axs[1].plot([i + start for i in range(len(sequence) + 1 - u + 1)], v, label = "{}, u={:d}".format(looptypes[k], u))
        axs[1].set_title("Unmodified")
        axs[1].set_xlabel("Sequence position")
        axs[1].set_ylabel("Probability to be unpaired")
        axs[1].legend()
    
        # create a dictionary of lists where the keys are the different loop types we distinguish
        d_diff = {}
        for k in data[u]:
            d_diff[k] = [v for v in map(lambda pair: pair[1] - pair[0], zip(data[u][k], data_unmod[u][k]))]
    
        for k, v in d_diff.items():
            axs[2].plot([i + start for i in range(len(sequence) + 1 - u + 1)], v, label = "{}, u={:d}".format(looptypes[k], u))
        axs[2].set_title("Difference")
        axs[2].set_xlabel("Sequence position")
        axs[2].legend(loc="upper left")

        modification_data = []

        for i in range(len(sequence) + 1 - u + 1):
            if i + 1 in modifications:
                modification_data.append(1)
            else:
                modification_data.append(0)
        
        axs[3].plot([i + start for i in range(len(sequence) + 1 - u + 1)], modification_data)
        axs[3].set_title("Modification Positions")
        axs[3].set_xlabel("Sequence position")
        axs[3].set_ylabel("Modifications")
        fig.subplots_adjust(hspace=0.4)
        fig.show()