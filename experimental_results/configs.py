



twirling_config_conjugate_by_CZ={'II':'II','IZ':'IZ','ZI':'ZI','ZZ':'ZZ',
                                'IY':'ZY','ZY':'IY','ZX':'IX','IX':'ZX',
                                'XI':'XZ','XZ':'XI','YI':'YZ','YZ':'YI',
                                'XY':'YX','YX':'XY','YY':'XX','XX':'YY'}

Is_test = False

# physical_qubits = ['q1','q2','q12','q13']


# if Is_test:
#     cz_gates_location_list = [('q6','q7','q5','q2','q8','q9','q4','q13'),('q3','q2','q5','q7','q1','q13','q4','q9')]
# else:

#     cz_gates_location_list = [('q1','q2','q12','q13')]
#     cz_gates_location_list += [('q1','q13','q2','q12')]


physical_qubits = ['q1','q2','q3','q4','q9','q10','q11','q12','q13']


if Is_test:
    cz_gates_location_list = [('q6','q7','q5','q2','q8','q9','q4','q13'),('q3','q2','q5','q7','q1','q13','q4','q9')]
else:

    cz_gates_location_list = [('q3','q2','q1','q13','q4','q9')]
    cz_gates_location_list += [('q12','q13','q1','q2','q11','q9'),('q10','q9','q11','q13','q4','q2')]




if Is_test:
    cycle_list = [0,1,2,3]
else:
    cycle_list = [0,1,2,3,4,5] # 这个是折叠的次数. 
basis_list0 = ['XX','XY','XZ','YX','YY','YZ','ZX','ZY','ZZ'] # 这个是对于一个 CZ gate 的测量的 basis. 
if Is_test:
    n_configs= 128 # 128*8 # 这个是 twirling 的次数. 
else:
    n_configs= 2


n_qubits=len(physical_qubits)


# 下面计算一下真实的输出 qubit 的次序 output_qubits
S0 = []
for index in physical_qubits:
    # print(int(index[1::]))
    S0.append(int(index[1::]))

S0.sort() 
print(f"S0: {S0}")
output_qubits = []
for index in S0:
    output_qubits.append(f"q{index}")
output_qubits = tuple(output_qubits)
print(f"output_qubits: {output_qubits}")
