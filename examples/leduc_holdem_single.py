''' A toy example of training single-agent algorithm on Leduc Hold'em
    The environment can be treated as normal OpenAI gym style single-agent environment
'''

import tensorflow as tf
import os
import numpy as np

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed, tournament
from rlcard.utils.logger import Logger

# Make environment
env = rlcard.make('leduc-holdem', config={'single_agent_mode':True})
eval_env = rlcard.make('leduc-holdem', config={'single_agent_mode':True})

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 1000
evaluate_num = 10000
timesteps = 100000

# The intial memory size
memory_init_size = 1000

# Train the agent every X steps
train_every = 1

# The paths for saving the logs and learning curves
log_dir = './experiments/leduc_holdem_single_dqn_result/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:

    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # Set up the agents
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_init_size=memory_init_size,
                     train_every=train_every,
                     state_shape=env.state_shape,
                     mlp_layers=[128,128])
    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

    state = env.reset()

    for timestep in range(timesteps):
        action = agent.step(state)
        next_state, reward, done = env.step(action)
        ts = (state, action, reward, next_state, done)
        agent.feed(ts)

        if timestep % evaluate_every == 0:
            rewards = []
            state = eval_env.reset()
            for _ in range(evaluate_num):
                action, _ = agent.eval_step(state)
                _, reward, done = env.step(action)
                if done:
                    rewards.append(reward)
            logger.log_performance(env.timestep, np.mean(rewards))

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('DQN')
    
    # Save model
    save_dir = 'models/leduc_holdem_single_dqn'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))
    