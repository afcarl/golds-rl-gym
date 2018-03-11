import argparse
import json

import gym
import numpy as np
import matplotlib.pyplot as plt
import fed_gym.envs.multiagent
from IPython import display
from matplotlib.animation import FuncAnimation



def hist_calc(x,Nsize):
    N=x.shape[0]
    u=np.zeros((Nsize,Nsize))
    amin=np.amin(x, axis=0)
    amax=np.amax(x, axis=0)
    xmin0=amin[0]
    xmax0=amax[0]+.000001
    xmin1=amin[1]
    xmax1=amax[1]+.000001
    for j in range(N):
        xs=np.int(np.floor(Nsize*(x[j][0]-xmin0)/(xmax0-xmin0)))
        ys=np.int(np.floor(Nsize*(x[j][1]-xmin1)/(xmax1-xmin1)))

        u[xs,ys]+=1
    return u

def update(idx):
    global x, xa

    action = actions[t]
    next_state, reward, done, _ = env.step(action)
    x = states[0]
    xa = states[1]

    make_plot(x, xa, colors) # plots a movie, turn off to speed up
    return x

def make_colors(N, Na):
    colors=[]
    for i in range(N):
        colors.append('dodgerblue')
    for i in range(Na):
        colors.append('tomato')
    return colors

def make_plot(x, xa, colors):
    plt.clf()
    xt=np.concatenate((x,xa),axis=0)
    plt.scatter(xt[:, 0], xt[:, 1],c=colors)
    plt.ylim((0, 5))
    # plt.yticks([])
    display.clear_output(wait=True)
    display.display(plt.gcf())


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--actions', type=str, default='swarm-eval.json')
    return parser


if __name__ == '__main__':
    args = get_arg_parser().parse_args()
    with open(args.actions, 'r') as f:
        actions_json = json.load(f)

    actions = np.array(actions_json['actions'])
    env = gym.envs.make("Swarm-eval-v0")
    states = env.reset()
    x = states[0]
    xa = states[1]
    colors = make_colors(80, 10)
    plt.style.use('ggplot')
    fig, ax = plt.subplots()

    done = False
    t = 0
    rewards = []
    for t in range(len(actions)):
        update(t)

    anim = FuncAnimation(fig, update, frames=np.arange(0, 128), interval=200)
    anim.save('line.gif', dpi=80, writer='imagemagick')


