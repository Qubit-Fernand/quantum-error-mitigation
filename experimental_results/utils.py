# 这个里面是最通用的函数. 

import gmpy2
from configs import *
import copy
import numpy as np

def gen_basis(num_qubits):
    data_sub = {}
    for i in range(2**num_qubits):
        sub_bin_str = bin(i)[2:].rjust(num_qubits,'0')
        data_sub[sub_bin_str] = 0

    basis = list(data_sub.keys())
    return basis


def map_config_bin_to_Pauli(config_temp,n_qubits):
    '''
    Return the n_qubits Pauli correspond to config_temp.
    
    config_temp: str which include the binary information of IXYZ.
    '''
    pauli_str=''
    for q in range(n_qubits):
        if config_temp[2*q:2*q+2]=='00':
            pauli_str+='I'
        elif config_temp[2*q:2*q+2]=='01':
            pauli_str+='X'
        elif config_temp[2*q:2*q+2]=='10':
            pauli_str+='Y'
        elif config_temp[2*q:2*q+2]=='11':
            pauli_str+='Z'
        else:
            raise Exception('Config mapping error.')
    return pauli_str


def generate_random_configurations(n_qubits,n_cycles,n_configs,random_state=None):
    '''
    Return n_configs numbers of random configurations for twirling and readout.
    
    Params
    ------------
    n_qubits, n_cycles, n_configs, random_state

    Returns
    ------------
    A list which includes all the configurations.
    For each tuple, the first n_cycles*2 strings are twirling configs, the last one is the readout config.

    Example
    ------------
    [(IX,XZ,ZY,YI,00),(YX,ZX,XZ,ZY,10),...] (n_qubits=2,n_cycles=2)
    '''
    if random_state is None:
        random_state=gmpy2.random_state(hash(gmpy2.random_state()))
    # The list can be mapped to a large integer in [0,4^(n_qubits*n_cycles*2*n_configs)*2^(n_qubits*n_configs))
    r_max=gmpy2.mpz(4)**(n_qubits*n_cycles*2*n_configs)*gmpy2.mpz(2)**(n_qubits*n_configs)
    config_num=gmpy2.mpz_random(random_state,r_max)
    # Transform the config_num into the tuple
    config_bin=gmpy2.digits(config_num,2)
    config_str=str(config_bin).rjust(n_configs*(2*n_qubits*2*n_cycles+n_qubits),'0')
    configs=[]
    for config_n in range(n_configs):
        config=[]
        for i in range(2*n_cycles):
            config_temp=config_str[config_n*n_qubits*(4*n_cycles+1)+i*n_qubits*2:config_n*n_qubits*(4*n_cycles+1)+(i+1)*n_qubits*2]
            twirl_str=map_config_bin_to_Pauli(config_temp,n_qubits)
            config.append(twirl_str)
        readout_bin=config_str[config_n*n_qubits*(4*n_cycles+1)+4*n_qubits*n_cycles:(config_n+1)*n_qubits*(4*n_cycles+1)]
        config.append(readout_bin)
        config=tuple(config)
        configs.append(config)
    return configs




# 如下是对于 learning CZ noise 模拟数据或者真机数据得到之后进行数值处理的函数. 


def int_to_binary_list(n: int, width: int = None) -> list:
    """
    将整数 n 转换为 0/1 组成的二进制列表。
    参数：
        n: 要转换的整数
        width: 输出二进制列表的总长度（自动左侧补零），默认为最小长度
    返回：
        binary_list: 由 0 和 1 组成的列表
    """
    if width is None:
        width = n.bit_length() if n > 0 else 1
    binary_str = f"{n:0{width}b}"
    binary_list = [int(bit) for bit in binary_str]
    return binary_list


def int_to_binary_array(n):
    # 转换为二进制字符串，去掉前缀 '0b'
    binary_str = bin(n)[2:]
    # 转换为整数列表
    binary_array = [int(bit) for bit in binary_str]
    # 统计 1 的个数
    ones_count = binary_array.count(1)
    return binary_array, ones_count




# 注意下面的这个函数高度依赖以来 learning-circuit 的结构.... 


def basis_pare(Is_Pauli_list,circuit_index,basis_list,cz_gates_location):
    # Is_Pauli_list 这一层还是对应的 physical qubit 的排序. 但是后面作用 GATE 的时候, 需要看cz_local 的位置了. 
    # 主打输入一个 Pauli word, 以及输出电路. 然后我们告诉他和这个 Pauli word 一对的另一个是谁. 
    circ_basis = basis_list[circuit_index] # 这个地方初始化的也是非常有问题的!!!!! 我现在只能说, 全是坑.... 不知道应该怎么修正了.... 本质是因为有的没有 CZ 的qubit 我没有初始化测量 base. 
    Pauli_pare1 = []
    for index in range(len(Is_Pauli_list)):
        if Is_Pauli_list[index] == 1:
            Pauli_pare1.append(circ_basis[index])
        else:
            Pauli_pare1.append('I')
    Pauli_pare2 = copy.deepcopy(Pauli_pare1)
    # 首先开始反方向作用 X. 
    # 如果其中包含了 X 或者 Y, 那么这个时候, 就会出现 S 

    # 反向走的话，先是经过 S 的 dagger 的 dagger, 然后经过 CZ 就得到了另一对. 
    coeff_s = 1
    if circuit_index in [0,1,3,4]:
        # 下面要作用 S 在 Pauli word 上面了
        for index in range(len(Pauli_pare1)):
            if Pauli_pare1[index] == 'X' and physical_qubits[index] in cz_gates_location:
                Pauli_pare2[index] = 'Y'
                # coeff_s *= -1
            elif Pauli_pare1[index] == 'Y' and physical_qubits[index] in cz_gates_location:
                Pauli_pare2[index] = 'X'
                coeff_s *= -1
            elif Pauli_pare1[index] == 'Z' and physical_qubits[index] in cz_gates_location:
                Pauli_pare2[index] = 'Z'
            elif Pauli_pare1[index] == 'I' and physical_qubits[index] in cz_gates_location:
                Pauli_pare2[index] = 'I'
            


    # 下面我们经过 CZ
    # print(Pauli_pare2)
    for index in range(len(cz_gates_location)//2):
        # physical_qubits.index(cz_gates_location[index*2])
        input_str = Pauli_pare2[physical_qubits.index(cz_gates_location[index*2])] + Pauli_pare2[physical_qubits.index(cz_gates_location[index*2+1])]
        # print(physical_qubits.index(cz_gates_location[index*2]))
        output_str = twirling_config_conjugate_by_CZ[input_str]
        Pauli_pare2[physical_qubits.index(cz_gates_location[index*2])] = output_str[0]
        Pauli_pare2[physical_qubits.index(cz_gates_location[index*2+1])] = output_str[1]

    # print(Pauli_pare2)

    # 到上一步结束, 完整的 Pauli_pare2 就算是生成了. 下面我们需要看看能不能回得去.... 
    Pauli_pare3 = copy.deepcopy(Pauli_pare2)
    if circuit_index in [0,1,3,4]:
        # 下面要作用 S 在 Pauli word 上面了
        for index in range(len(Pauli_pare1)):
            if Pauli_pare2[index] == 'X' and physical_qubits[index] in cz_gates_location:
                Pauli_pare3[index] = 'Y'
                # coeff_s *= -1
            elif Pauli_pare2[index] == 'Y' and physical_qubits[index] in cz_gates_location:
                Pauli_pare3[index] = 'X'
                coeff_s *= -1
            elif Pauli_pare2[index] == 'Z' and physical_qubits[index] in cz_gates_location:
                Pauli_pare3[index] = 'Z'
            elif Pauli_pare2[index] == 'I' and physical_qubits[index] in cz_gates_location:
                Pauli_pare3[index] = 'I'
    # for index in range(len(Pauli_pare1)//2):
    #     input_str = Pauli_pare3[index*2] + Pauli_pare3[index*2+1]
    #     output_str = twirling_config_conjugate_by_CZ[input_str]
    #     Pauli_pare3[index*2] = output_str[0]
    #     Pauli_pare3[index*2+1] = output_str[1]

    for index in range(len(cz_gates_location)//2):
        # physical_qubits.index(cz_gates_location[index*2])
        input_str = Pauli_pare3[physical_qubits.index(cz_gates_location[index*2])] + Pauli_pare3[physical_qubits.index(cz_gates_location[index*2+1])]
        output_str = twirling_config_conjugate_by_CZ[input_str]
        Pauli_pare3[physical_qubits.index(cz_gates_location[index*2])] = output_str[0]
        Pauli_pare3[physical_qubits.index(cz_gates_location[index*2+1])] = output_str[1]


    # 我们还要注意, 如果插入了 S gate 的话, 到底还是不是两个 Pauli pair 是一组了. 是不是可能出现多个. 
    if Pauli_pare3 == Pauli_pare1:
        # 说明是一个 Pauli pair
        return Pauli_pare1, Pauli_pare2
    
    else:
        print("Pauli_pare1:", Pauli_pare1)
        print("Pauli_pare2:", Pauli_pare2)
        print("Pauli_pare3:", Pauli_pare3)
        print("circuit_index:", circuit_index)
        raise ValueError("Pauli pair is not a pair anymore, please check the code.")
    


# 上面的这个函数, 我们可能需要引入 basis_list_gate... 这个变量来进行进一步的处理了... 
    

def scale_list_Pauli_word(circuit_index,Is_Pauli_list,data_np_retw):
    output_list1 = [0]*len(cycle_list)
    wndex0 = 0
    for index in range(len(cycle_list)*circuit_index, len(cycle_list)*(circuit_index+1)):
        data_np_retw0 = data_np_retw[index].sum(axis=0)


        # print("data_np_retw0:", data_np_retw0.shape)
        for jndex in range(data_np_retw0.shape[0]):
            qubit_idx= int_to_binary_list(jndex,n_qubits) # 这个地方需要进行事后核对一下的. 
            # print(qubit_idx)
            S0 = 0
            for windex in range(len(qubit_idx)):
                if qubit_idx[windex] == 1 and Is_Pauli_list[windex] == 1:
                    S0 += 1
            if S0 % 2 == 0:
                output_list1[wndex0] += data_np_retw0[jndex]
            else:
                output_list1[wndex0] -= data_np_retw0[jndex]

        output_list1[wndex0] /= data_np_retw0.sum()
        wndex0 += 1
        # print(data_np_retw0.sum())

    return output_list1

def list2str(Pauli_pare):
    output0 = ""
    for index in range(len(Pauli_pare)):
        output0 += Pauli_pare[index]
    return output0


def fit_exponential(x, y):
    """
    最小二乘拟合函数 f(x) = a * b^x
    输入：
        x: 一维 numpy 数组，输入自变量
        y: 一维 numpy 数组，目标值（必须 > 0）
    返回：
        a, b: 拟合得到的系数
    """
    x = np.array(copy.deepcopy(x)).reshape(-1)
    y = np.array(copy.deepcopy(y)).reshape(-1)
    # if np.any(y <= 0):
    #     raise ValueError("All y values must be > 0 for log-transform.")

    
    

    if np.any(y <= 0):
        x_new = []
        y_new = []
        for index in range(y.shape[0]):
            if y[index] > 0:
                x_new.append(x[index])
                y_new.append(y[index])
        x = np.array(x_new)
        y = np.array(y_new)
        print("All y values must be > 0 for log-transform.")

    log_y = np.log(y)
    A = np.vstack([np.ones_like(x), x]).T
    c, residuals, _, _ = np.linalg.lstsq(A, log_y, rcond=None)
    
    log_a, log_b = c[0], c[1]
    a, b = np.exp(log_a), np.exp(log_b)
    return a, b


print("Import new one!!")




def is_commuting(Pauli_word1, Pauli_word2):
    """
    判断两个 Pauli word 是否交换。
    参数：
        Pauli_word1: 第一个 Pauli word 字符串
        Pauli_word2: 第二个 Pauli word 字符串
    返回：
        bool: 如果两个 Pauli word 交换，返回 True；否则返回 False。
    """
    # 检查两个 Pauli word 的长度是否相同
    if len(Pauli_word1) != len(Pauli_word2):
        return False
    S = 1
    # 检查每个对应位置的 Pauli 字符是否满足交换关系
    for p1, p2 in zip(Pauli_word1, Pauli_word2):
        if p1 == 'I' or p2 == 'I':
            continue  # I 与任何 Pauli 字符都交换
        elif p1 == p2:
            continue  # 相同的 Pauli 字符交换

        elif p1 == 'X' and p2 == 'Y':
            S *= -1
        elif p1 == 'X' and p2 == 'Z':
            S *= -1
        elif p1 == 'Y' and p2 == 'X':
            S *= -1
        elif p1 == 'Y' and p2 == 'X':
            S *= -1
        elif p1 == 'Y' and p2 == 'Z':
            S *= -1
        elif p1 == 'Z' and p2 == 'Y':
            S *= -1
        elif p1 == 'Z' and p2 == 'X':
            S *= -1

        else:
            raise ValueError(f"Pauli word {Pauli_word1} and {Pauli_word2} are not commuting.")

    
    return S