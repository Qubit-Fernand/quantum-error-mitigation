from configs import *


class Base_Circuit:
    def H_gate(self, index):
        pass
    def hadamard(self, index):
        pass
    def X_gate(self, index):
        pass
    def Y_gate(self, index):
        pass
    def Z_gate(self, index):
        pass
    def I_gate(self, index):
        pass
    def S_gate(self, index):
        pass
    def S_dagger_gate(self, index):
        pass
    def CZ_gate(self, index1, index2):
        pass
    def prepare_initial_state(self, prepare_info):
        pass
    def rotate_to_measurement_basis(self, measure_info):
        pass
    def random_bit_flip(self, random_info):
        pass
    def add_global_barrier(self):
        # 这个是无脑在全部的 qubit 和 coupler 上加入 twirling 的功能. 
        pass

    def add_noise(self):
        # 这个只有模拟器中生效, 真机上不用管这个功能的... 
        pass

    def get_qubits(self, qubits):
        # 存储 qubits 的信息

        pass
    def get_cz_gates_qubits(self, cz_gates_qubits):
        # 存储 cz_gates_qubits 的信息

        pass





def twirling(circuit: Base_Circuit,twirling_config:str,qubits:list,cz_gates_qubits,conjugate=False,global_twirling=False):
    '''
    Apply the twirling operation on the physical qubits according to the 2-qubit gates' location.
    '''
    n_cz_gates=int(len(cz_gates_qubits)/2)
    for n_cp in range(n_cz_gates):
        q_cp_0=cz_gates_qubits[2*n_cp]
        q_cp_1=cz_gates_qubits[2*n_cp+1]
        index_cp_0=qubits.index(q_cp_0)
        index_cp_1=qubits.index(q_cp_1)
        q_cp=(q_cp_0,q_cp_1)
        cp_twirling_config=twirling_config[index_cp_0]+twirling_config[index_cp_1]
        if conjugate is False:
            config=cp_twirling_config
        else:
            config=twirling_config_conjugate_by_CZ[cp_twirling_config]
        
        for i in range(2):
            if config[i]=='I':
                continue
            elif config[i]=='X':
                circuit.X_gate(qubits.index(q_cp[i]))
                # alg += X.on(qubits.index(q_cp[i]))
                # alg[gates.PiPulse([q_cp[i]])]
            elif config[i]=='Y':
                circuit.Y_gate(qubits.index(q_cp[i]))
                # alg += Y.on(qubits.index(q_cp[i]))
                # alg[gates.PiPulse([q_cp[i]],phase=np.pi/2.)]
            elif config[i]=='Z':
                circuit.Z_gate(qubits.index(q_cp[i]))
                # alg += Z.on(qubits.index(q_cp[i]))
                # alg[gates.VirtualZ([q_cp[i]],np.pi)]
            else:
                raise Exception("Twirling configuration error.")
    
    if global_twirling is True:
        for i in range(len(qubits)):
            if qubits[i] not in cz_gates_qubits:
                # print("全局twirling 生效了")
                # print(qubits[i])
                if twirling_config[i]=='I':
                    continue
                elif twirling_config[i]=='X':
                    # alg[gates.PiPulse([qubits[i]])]
                    # alg += X.on(i)
                    circuit.X_gate(i)
                elif twirling_config[i]=='Y':
                    # alg[gates.PiPulse([qubits[i]],phase=np.pi/2.)]
                    # alg += Y.on(i)
                    circuit.Y_gate(i)
                elif twirling_config[i]=='Z':
                    # alg[gates.VirtualZ([qubits[i]],np.pi)]
                    circuit.Z_gate(i)
                    # alg += Z.on(i)
                else:
                    raise Exception("Twirling configuration error.")

def construction_cz_gate(circuit:Base_Circuit,circuits_information, random_config_tuple,measure:list,cz_gates_location:tuple,Is_twirling=True):

    '''
    circuit: 一个初始化之后的空的电路. 
    construction learning circuit, 按照 circuits_information 里面的内容来进行构造.
    circuits_information[0] 表示的是 prepare state 的 basis, circuits_information[1] 表示的是 cycle 的次数.
    在 refactoring3 的版本之后, 我们扩展了 circuits_information 的内容, 包含了是否插入 S 和 H gate 的信息... 
    circuits_information[2]: boolean, True 表示插入 S
    circuits_information[3]: boolean, True 表示插入 H
    S 和 H gate 仅仅插入在 CZ 关联的 qubits 上面!!!!
    这里的设置直接影响后面learning noise 的时候, fidelity pair 的计算方式... 
    '''

    for wwndex in range(len(physical_qubits)):
        circuit.I_gate(wwndex) # 这个是确保 mindspore 中每个 qubit 都能被很好的使用到

    
    qubits=[]
    for i in range(len(physical_qubits)):
        # print('measure[i]:', measure[i])
        # print('true', circuit.circuit.agents[measure[i]])
        qubits.append(measure[i])
    cz_gates_qubits=[]
    for q_str in cz_gates_location:
        cz_gates_qubits.append(qubits[physical_qubits.index(q_str)])

    circuit.get_qubits(qubits)
    circuit.get_cz_gates_qubits(cz_gates_qubits)

    

    circuit.prepare_initial_state(circuits_information[0])

    for i in range(int(circuits_information[1])):



        if circuits_information[3] is True:
            for j in range(len(cz_gates_location)//2):
                index_1=physical_qubits.index(cz_gates_location[2*j])
                index_2=physical_qubits.index(cz_gates_location[2*j+1])

                sub_basis=circuits_information[0][index_1]+circuits_information[0][index_2]


                circuit.H_gate(qubits.index(cz_gates_qubits[2*j]))
                circuit.H_gate(qubits.index(cz_gates_qubits[2*j+1]))



        # Apply twirling gate
        if Is_twirling:
            twirling(circuit,random_config_tuple[2*i],qubits,cz_gates_qubits,conjugate=False,global_twirling=True)


        # 加入对齐
        circuit.add_global_barrier()
        

        # Apply CZ gate
        for k in range(int(len(cz_gates_location)/2)):
            circuit.CZ_gate(qubits.index(cz_gates_qubits[2*k]), qubits.index(cz_gates_qubits[2*k+1]))


            # alg += Z.on(qubits.index(cz_gates_qubits[2*k]), qubits.index(cz_gates_qubits[2*k+1]))

        # 加入对齐
        circuit.add_global_barrier()





        
        # Apply CZ conjugated twirling gate
        if Is_twirling:
            twirling(circuit,random_config_tuple[2*i],qubits,cz_gates_qubits,conjugate=True,global_twirling=True)

        # Apply S_j gates if sub-basis is XY, YX, XX, YY. 这个地方我们需要进行分类讨论了.... 可能需要给 circuit_information 加入几个维度来控制这个事情才可以. 
        if circuits_information[2] is True:
            # 这里表示我们需要插入 S gate
            



        
            for j in range(len(cz_gates_location)//2):
                index_1=physical_qubits.index(cz_gates_location[2*j])
                index_2=physical_qubits.index(cz_gates_location[2*j+1])

                sub_basis=circuits_information[0][index_1]+circuits_information[0][index_2]
                # if sub_basis in ['XY','YX','XX','YY']:
                #     # Apply S_c S_t
                #     # alg[gates.VirtualZ([cz_gates_qubits[2*j]],-np.pi/2)]
                #     # alg[gates.VirtualZ([cz_gates_qubits[2*j+1]],-np.pi/2)]

                circuit.S_gate(qubits.index(cz_gates_qubits[2*j]))
                circuit.S_gate(qubits.index(cz_gates_qubits[2*j+1]))

                # alg += S.on(qubits.index(cz_gates_qubits[2*j]))
                # alg += S.on(qubits.index(cz_gates_qubits[2*j+1]))

        


        # Apply twirling gate
        if Is_twirling:
            twirling(circuit,random_config_tuple[2*i+1],qubits,cz_gates_qubits,conjugate=False,global_twirling=True)
        
        
        # # 在之前加入对齐功能: 
        # # for k in range()
        # sync_list = []
        # for kndex in range(len(couplers)):
        #     sync_list.append(couplers[kndex])

        # for kndex in range(n_qubits):
        #     sync_list.append(qubits[kndex])

        # alg[gates.Sync(sync_list)]

        circuit.add_global_barrier()
        
        
        
        
        # Apply CZ gate
        for k in range(int(len(cz_gates_location)/2)):
            # sync_list=qubits.copy()
            # sync_list=[cz_gates_qubits[2*k], cz_gates_qubits[2*k+1]]
            # sync_list.append(couplers[k])
            # alg[gates.Sync(sync_list)]
            # alg[gates.CpSwapCZ([cz_gates_qubits[2*k], cz_gates_qubits[2*k+1]])]
            # alg[gates.Sync(sync_list)]

            circuit.CZ_gate(qubits.index(cz_gates_qubits[2*k]), qubits.index(cz_gates_qubits[2*k+1]))

            # alg += Z.on(qubits.index(cz_gates_qubits[2*k]), qubits.index(cz_gates_qubits[2*k+1]))

        circuit.add_global_barrier()




        # # 在之前加入对齐功能: 
        # # for k in range()
        # sync_list = []
        # for kndex in range(len(couplers)):
        #     sync_list.append(couplers[kndex])

        # for kndex in range(n_qubits):
        #     sync_list.append(qubits[kndex])

        # alg[gates.Sync(sync_list)]



            
        # Apply CZ conjugated twirling gate
        if Is_twirling:
            twirling(circuit,random_config_tuple[2*i+1],qubits,cz_gates_qubits,conjugate=True,global_twirling=True)

        if circuits_information[2] is True:
            # 这里表示我们需要插入 S gate
            



        
            for j in range(len(cz_gates_location)//2):
                index_1=physical_qubits.index(cz_gates_location[2*j])
                index_2=physical_qubits.index(cz_gates_location[2*j+1])

                sub_basis=circuits_information[0][index_1]+circuits_information[0][index_2]
                # if sub_basis in ['XY','YX','XX','YY']:
                #     # Apply S_c S_t
                #     # alg[gates.VirtualZ([cz_gates_qubits[2*j]],-np.pi/2)]
                #     # alg[gates.VirtualZ([cz_gates_qubits[2*j+1]],-np.pi/2)]

                circuit.S_dagger_gate(qubits.index(cz_gates_qubits[2*j]))
                circuit.S_dagger_gate(qubits.index(cz_gates_qubits[2*j+1]))

                # alg += S.on(qubits.index(cz_gates_qubits[2*j]))
                # alg += S.on(qubits.index(cz_gates_qubits[2*j+1]))

        if circuits_information[3] is True:
            for j in range(len(cz_gates_location)//2):
                index_1=physical_qubits.index(cz_gates_location[2*j])
                index_2=physical_qubits.index(cz_gates_location[2*j+1])

                sub_basis=circuits_information[0][index_1]+circuits_information[0][index_2]


                circuit.H_gate(qubits.index(cz_gates_qubits[2*j]))
                circuit.H_gate(qubits.index(cz_gates_qubits[2*j+1]))


        # # Apply S_j^dagger gates if basis is XY, YX, XX, YY
        # for j in range(len(cz_gates_location)//2):
        #     index_1=physical_qubits.index(cz_gates_location[2*j])
        #     index_2=physical_qubits.index(cz_gates_location[2*j+1])
        #     sub_basis=circuits_information[0][index_1]+circuits_information[0][index_2]
        #     # print("index_1:", index_1)
        #     # print("index_2:", index_2)
        #     # print("sub_basis:", sub_basis)
        #     if sub_basis in ['XY','YX','XX','YY']:
        #         # Apply S_c S_t
        #         # alg[gates.VirtualZ([cz_gates_qubits[2*j]],np.pi/2)]
        #         # alg[gates.VirtualZ([cz_gates_qubits[2*j+1]],np.pi/2)]
        #         alg += S.on(qubits.index(cz_gates_qubits[2*j]))
        #         alg += S.on(qubits.index(cz_gates_qubits[2*j+1]))
        #         alg += Z.on(qubits.index(cz_gates_qubits[2*j]))
        #         alg += Z.on(qubits.index(cz_gates_qubits[2*j+1]))
                







    # Rotate to measurement basis
    circuit.rotate_to_measurement_basis(circuits_information[0])
    # Apply random bit flip gate for readout error mitigation
    circuit.random_bit_flip(random_config_tuple[-1])


    circuit.add_noise()