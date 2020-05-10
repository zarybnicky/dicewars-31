import numpy as np
from os.path import dirname
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from torch.utils.data import Dataset, DataLoader

class AttacksDataset(Dataset):
    def __init__(self, csv_file):
        self.data = np.genfromtxt(csv_file, delimiter=',')

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        return (torch.from_numpy(self.data[idx, :-2]).float(),
                torch.from_numpy(self.data[idx, -2:]).float())

def main():
    model = nn.Sequential(
        nn.Linear(21, 13),
        nn.PReLU(),
        nn.Linear(13, 8),
        nn.PReLU(),
        nn.Linear(8, 2),
        nn.Sigmoid(),
    )
    dataset = AttacksDataset(dirname(__file__) + '/turns.csv')
#    optimizer = optim.Adam(model.parameters())
    optimizer = optim.RMSprop(model.parameters())
    loss_fn = nn.BCELoss()
    batch_size = 50
    loader = torch.utils.data.DataLoader(dataset=dataset, shuffle=True, batch_size=batch_size)

    for epoch in range(2000):
        total_loss = 0
        for batch_idx, (x, target) in enumerate(loader):
            optimizer.zero_grad()
            out = model(x)
            loss = loss_fn(out, target)
            total_loss += loss.data.item()
            loss.backward()
            optimizer.step()
        print('epoch: {}, train success: {:.6f}%'.format(epoch, 100 - total_loss * batch_size * 100 / len(dataset)))

    torch.save(model.state_dict(), dirname(__file__) + '/local-predictor.model')

if __name__ == '__main__':
    main()
