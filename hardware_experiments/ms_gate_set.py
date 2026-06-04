
import numpy as np

import itertools
import copy
from mindquantum.core.circuit import Circuit, UN
from mindquantum.core.gates import H, Rzz, RX, RZ, X, S, Z, I, Y, RY,DepolarizingChannel, PauliChannel
from mindquantum.core.operators import Hamiltonian, QubitOperator
from mindquantum.framework import MQAnsatzOnlyLayer
from mindquantum.simulator import Simulator
import networkx as nx
import mindspore.nn as nn
from mindquantum.core.parameterresolver import PRGenerator


from mindspore import nn
from mindquantum.framework import MQOps

from mindquantum.framework import MQAnsatzOnlyOps
from mindspore.common.initializer import initializer, One
from mindspore import Parameter, Tensor, ops, nn
import mindspore as ms
import mindspore.dataset as ds

import multiprocessing


from mindquantum.core.gates import Measure   
from collections import Counter
import itertools

# from utils import *

import random

# 下面导入公共的常数
from configs import *

from basis_circuit import *




class MQ_Circuit(Base_Circuit):
    def __init__(self,qubits_num):
        self.qubits_num = qubits_num
        self.circuit = Circuit()
        self.qubits = []
        self.cz_gates_qubits = []
        self.sim = Simulator("mqmatrix",qubits_num)

        self.circ_measure = Circuit()

        for index in range(qubits_num):
            self.circ_measure += Measure(f"q{index}").on(index)

    def hadamard(self, index):
        self.circuit += H.on(index)

    def H_gate(self, index):
        self.circuit += H.on(index)


    def X_gate(self, index):
        self.circuit += X.on(index)
        
    def Y_gate(self, index):
        self.circuit += Y.on(index)
        
    def Z_gate(self, index):
        self.circuit += Z.on(index)
        
    def I_gate(self, index):
        self.circuit += I.on(index)
        
    def S_gate(self, index):
        self.circuit += S.on(index)
        
    def S_dagger_gate(self, index):
        self.circuit += S.on(index)
        self.circuit += Z.on(index)
        
    def CZ_gate(self, index1, index2):
        self.circuit += Z.on(index1, index2)
        
    def prepare_initial_state(self, prepare_info):
        for i in range(self.qubits_num):
            if prepare_info[i] == 'Z':
                continue
            elif prepare_info[i] == 'X':
                self.hadamard(i)
                

            elif prepare_info[i] == 'Y':
                self.Z_gate(i)
                self.H_gate(i)
                self.S_gate(i)

                # alg += Z.on(qubits.index(qubits[i]))
                # alg += H.on(qubits.index(qubits[i]))
                # alg += S.on(qubits.index(qubits[i]))

            else:
                raise Exception("State preparation error.")

        
    def rotate_to_measurement_basis(self, measure_info):
        for i in range(self.qubits_num):
            if measure_info[i] == 'Z':
                continue
            elif measure_info[i] == 'X':
                self.hadamard(i)
                # hadamard(alg, qubits[i],qubits)
            elif measure_info[i] == 'Y':
                self.S_gate(i)
                self.Z_gate(i)
                self.H_gate(i)
                # alg += S.on(qubits.index(qubits[i]))

                # alg += Z.on(qubits.index(qubits[i]))
                # alg += H.on(qubits.index(qubits[i]))
            else:
                raise Exception("Measurement basis transformation error.")

    def random_bit_flip(self, random_info):
        for i in range(self.qubits_num):
            if random_info[i] == '0':
                continue
            elif random_info[i] == '1':
                # alg += X.on(i)
                self.X_gate(i)
                # alg[gates.PiPulse([qubits[i]])]
            else:
                raise Exception("Random bit flip error.")
        
    def add_global_barrier(self):
        # 这个是无脑在全部的 qubit 和 coupler 上加入 twirling 的功能. 
        self.circuit.barrier()


    def add_noise(self):
        # 这个只有模拟器中生效, 真机上不用管这个功能的... 
        self.circuit = noise_sim_mq(self.circuit)



    def get_qubits(self, qubits):
        # 存储 qubits 的信息
        self.qubits = qubits

        
    def get_cz_gates_qubits(self, cz_gates_qubits):
        # 存储 cz_gates_qubits 的信息
        self.cz_gates_qubits = cz_gates_qubits


    def sampling(self, shots = 1024*16):
        self.sim.reset()
        self.sim.apply_circuit(self.circuit)
        
        return self.sim.sampling(self.circ_measure, shots = shots)

        

        

    def __str__(self):
        # return f"qwerqwer{self.qubits_num}"
        return self.circuit.__str__()
    
    
    










    
class T_Circuit(Base_Circuit):
    def __init__(self,qubits_num):
        self.qubits_num = qubits_num
        self.circuit = Circuit()

    def hadamard(self, index):
        self.circuit += H.on(index)

    def __str__(self):
        return str(self.circuit)



    

def noise_sim_mq(circ):
    circ_noise = Circuit()
    if isinstance(circ, str):
        # print("circ 是字符串")
        circ = Circuit.from_openqasm(circ)
        # print(circ)


    
    for gate in circ:
        if len(gate.obj_qubits + gate.ctrl_qubits) >= 2:
            # 加入 noise, noise 需要加入在 gate 之前
            for index in gate.obj_qubits + gate.ctrl_qubits:
                circ_noise += PauliChannel(0, 0, 0.01).on(index)
                circ_noise += PauliChannel(0.01, 0, 0).on(index)


        # print(gate.obj_qubits,gate.ctrl_qubits)
        circ_noise += gate

    return circ_noise



def hadamard(alg, q, qubits):
    '''
    Apply hadamard gate on qubit q.
    H=ry(pi/2)rz(pi)
    '''
    # Apply rz(pi) first
    alg += H.on(qubits.index(q))
    # alg[gates.VirtualZ([q],np.pi)]
    # alg[gates.PiHalfPulse([q], phase=np.pi / 2.)]


def X_gate(alg, q, qubits):
    alg += X.on(qubits.index(q))

def Y_gate(alg, q, qubits):
    alg += Y.on(qubits.index(q))

def Z_gate(alg, q, qubits):
    alg += Z.on(qubits.index(q))


def I_gate(alg, q, qubits):
    alg += I.on(qubits.index(q))


def S_gate(alg, q, qubits):
    alg += S.on(qubits.index(q))



# H = PiHalfPulse * S * Z
# H*S = PiHalfPulse

# H = PiHalfPulse * Z


def prepare_initial_state(alg, prepare_info, qubits:list):
    for i in range(len(qubits)):
        if prepare_info[i] == 'Z':
            continue
        elif prepare_info[i] == 'X':
            hadamard(alg, qubits[i],qubits)
        elif prepare_info[i] == 'Y':
            # alg[gates.PiHalfPulse([qubits[i]], phase=np.pi / 2.)]
            alg += Z.on(qubits.index(qubits[i]))
            alg += H.on(qubits.index(qubits[i]))
            alg += S.on(qubits.index(qubits[i]))
            # alg[gates.VirtualZ([qubits[i]], -np.pi/2.)]
        else:
            raise Exception("State preparation error.")


def rotate_to_measurement_basis(alg, measure_info, qubits:list):
    for i in range(len(qubits)):
        if measure_info[i] == 'Z':
            continue
        elif measure_info[i] == 'X':
            hadamard(alg, qubits[i],qubits)
        elif measure_info[i] == 'Y':
            alg += S.on(qubits.index(qubits[i]))
            # alg[gates.VirtualZ([qubits[i]], -np.pi/2)]
            # alg[gates.PiHalfPulse([qubits[i]], phase=np.pi / 2.)]
            alg += Z.on(qubits.index(qubits[i]))
            alg += H.on(qubits.index(qubits[i]))
        else:
            raise Exception("Measurement basis transformation error.")


def random_bit_flip(alg, random_info, qubits:list):
    for i in range(len(qubits)):
        if random_info[i] == '0':
            continue
        elif random_info[i] == '1':
            alg += X.on(i)
            # alg[gates.PiPulse([qubits[i]])]
        else:
            raise Exception("Random bit flip error.")

if __name__ == "__main__":
    def test_mq_circuit(circuit: Base_Circuit):
        circuit.hadamard(0)
        circuit.hadamard(1)
        print(circuit)
        print(circuit.circuit)
    circ = MQ_Circuit(2)
    test_mq_circuit(circ)
    print(circ)
    # test_mq_circuit(T_Circuit(2))

    # circ = Base_Circuit()
    # print(circ)
