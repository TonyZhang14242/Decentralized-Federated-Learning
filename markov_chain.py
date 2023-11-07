import random


def generate_markov_chain(pattern_name, transition_probability, number_of_states, number_of_time_slot):
    # parameter:pattern_name,transition_probability
    # return:list: states list
    markov_chain = []

    # initial state
    markov_chain.append(random.randint(0, number_of_states - 1))  # 随机挑选一个状态.状态从0开始
    if pattern_name == 'periodic':
        for iter in range(number_of_time_slot - 1):
            # 抽取0到1的随机数
            transfer = random.random()
            if transfer < transition_probability:
                markov_chain.append(markov_chain[-1])  # 保持上一个状态
            else:
                next_state = (markov_chain[-1] + 1) % number_of_states
                markov_chain.append(next_state)
    if pattern_name == 'gradual':
        for iter in range(number_of_time_slot - 1):
            # 抽取0到1的随机数
            transfer = random.random()
            if transfer < transition_probability:
                next_state = (markov_chain[-1] + 1) % number_of_states
                markov_chain.append(next_state)  # 下一个状态
            else:
                next_state = (markov_chain[-1] - 1) % number_of_states
                markov_chain.append(next_state)  # 上一个状态
    if pattern_name == 'random':
        for iter in range(number_of_time_slot - 1):
            markov_chain.append(random.randint(0, number_of_states - 1))

    return markov_chain


if __name__ == '__main__':
    mc = generate_markov_chain(pattern_name='gradual', transition_probability=0.5, number_of_states=10,
                               number_of_time_slot=20)
    print(mc)
    # with open('./seq.txt', 'w') as f:
    #     f.write(str(mc[0]))
    #     for i in range(1, len(mc)):
    #         f.write(f',{mc[i]}')
