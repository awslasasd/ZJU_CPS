import struct

# 辅助函数，用于无符号32位算术运算
def u32(x):
    return x & 0xFFFFFFFF

# 加密过程中使用的常量
CONSTANTS_C = [
    u32(1579382783),    # 0x5E2587FF
    u32(-1136201730),   # 0xBCDEF01E
    u32(443181053),     # 0x1A6B77FD
    u32(2022563836),    # 0x788E07FC
    u32(-693020677),    # 0xD6B70B7B
    u32(886362106),     # 0x34D579FA
    u32(-1829222407),   # 0x92F5F5F9
    u32(-249839624)     # 0xF1234578
]
def f_transform(val, k_part_cycle1, k_part_cycle0, delta_const):
    term1 = u32(k_part_cycle1 + (val >> 5))
    term2 = u32(val + delta_const)
    term3 = u32(k_part_cycle0 + u32(16 * val))
    return u32(term1 ^ term2 ^ term3)

# --- 密钥派生 ---
dword_4143D8_bytes = [0x64, 0x96, 0x50, 0x16, 0x69, 0xFF, 0xBE, 0x60]

# 初始密钥字符串: "IamTheKeyYouKnow" 
key_material_bytes = bytearray(b"IamTheKeyYouKnow")

# 对前15个字节进行异或操作
for i in range(15):
    key_material_bytes[i] ^= dword_4143D8_bytes[i % 8]

# 修改后的 key_material_bytes 的前16个字节构成 v20
# v20 是一个包含4个DWORD的数组
v20_key = []
for i in range(4):
    v20_key.append(struct.unpack('<I', key_material_bytes[i*4 : i*4+4])[0])

# --- 加密数据 ---
# byte_414060 数组
byte_414060_hex = [
    0xDC, 0x45, 0x1E, 0x03, 0x89, 0xE9, 0x76, 0x27,
    0x47, 0x48, 0x23, 0x01, 0x70, 0xD2, 0xCE, 0x64,
    0xDA, 0x7F, 0x46, 0x33, 0xB1, 0x03, 0x49, 0xA3,
    0x27, 0x00, 0xD1, 0x2C, 0x37, 0xB3, 0xBD, 0x75
]

# 将加密的字节数组转换为DWORD列表
encrypted_dwords = []
for i in range(0, len(byte_414060_hex), 4):
    encrypted_dwords.append(struct.unpack('<I', bytes(byte_414060_hex[i:i+4]))[0])

# --- 一对DWORD的解密函数 ---
def decrypt_block_pair(enc_x0_dword, enc_x1_dword, key_v20_parts, C_constants):
    # 步骤 0: 撤销加密最后一步的与 0xF 的异或操作
    # EncX0_prime 是 (v6_expr)，EncX1_prime 是 v5
    val_L_final_stage = u32(enc_x0_dword ^ 0xF) # 这是加密时的 (v6 + f(v2, k1,k0, C8))
    val_R_final_stage = u32(enc_x1_dword ^ 0xF) # 这是加密时的 v5

    # 逆向执行17个计算步骤 (从 v5, v_temp_L_for_v5 回到 X0, X1)
    # 所有减法都是模 2^32 (u32函数处理此问题)

    # v5 的原始计算 (加密步骤17):
    # v5 = v2 + f(v_temp_L_for_v5, k[3], k[2], C8)
    # 此处, v_temp_L_for_v5 是 val_L_final_stage。 val_R_final_stage 是 v5。
    # 所以, v2 = v5 - f(v_temp_L_for_v5, k[3], k[2], C8)
    v2 = u32(val_R_final_stage - f_transform(val_L_final_stage, key_v20_parts[3], key_v20_parts[2], C_constants[7]))

    # v_temp_L_for_v5 的原始计算 (加密步骤16):
    # v_temp_L_for_v5 = v6 + f(v2, k[1], k[0], C8)
    # 所以, v6 = v_temp_L_for_v5 - f(v2, k[1], k[0], C8)
    v6 = u32(val_L_final_stage - f_transform(v2, key_v20_parts[1], key_v20_parts[0], C_constants[7]))
    
    # 逆向序列 (v2,v6 -> v7,v8 -> ... -> v16,v17 -> X0,X1)
    # 常量通过 C_constants[6] (对应C7) 到 C_constants[0] (对应C1) 索引

    # 涉及 C7 (索引 6) 的操作
    v7 = u32(v2 - f_transform(v6, key_v20_parts[3], key_v20_parts[2], C_constants[6]))
    v8 = u32(v6 - f_transform(v7, key_v20_parts[1], key_v20_parts[0], C_constants[6]))

    # 涉及 C6 (索引 5) 的操作
    v9 = u32(v7 - f_transform(v8, key_v20_parts[3], key_v20_parts[2], C_constants[5]))
    v10 = u32(v8 - f_transform(v9, key_v20_parts[1], key_v20_parts[0], C_constants[5]))

    # 涉及 C5 (索引 4) 的操作
    v11 = u32(v9 - f_transform(v10, key_v20_parts[3], key_v20_parts[2], C_constants[4]))
    v1_val = u32(v10 - f_transform(v11, key_v20_parts[1], key_v20_parts[0], C_constants[4])) # 这是C代码中的 'v1'

    # 涉及 C4 (索引 3) 的操作
    v12 = u32(v11 - f_transform(v1_val, key_v20_parts[3], key_v20_parts[2], C_constants[3]))
    # v_temp_L_for_v12 在加密时是: v14 + f(v13, k[1],k[0], C3)
    # v1_val 在加密时是 v_temp_L_for_v12 + f(v12, k[1],k[0], C4)
    # 所以, v_temp_L_for_v12 = v1_val - f(v12, k[1],k[0], C4)
    v_temp_L_for_v12 = u32(v1_val - f_transform(v12, key_v20_parts[1], key_v20_parts[0], C_constants[3]))

    # 涉及 C3 (索引 2) 的操作
    # v12 在加密时是 = v13 + f(v_temp_L_for_v12, k[3],k[2], C3)
    v13 = u32(v12 - f_transform(v_temp_L_for_v12, key_v20_parts[3], key_v20_parts[2], C_constants[2]))
    # v_temp_L_for_v12 在加密时是 = v14 + f(v13, k[1],k[0], C3)
    v14 = u32(v_temp_L_for_v12 - f_transform(v13, key_v20_parts[1], key_v20_parts[0], C_constants[2]))

    # 涉及 C2 (索引 1) 的操作
    v15 = u32(v13 - f_transform(v14, key_v20_parts[3], key_v20_parts[2], C_constants[1]))
    v16 = u32(v14 - f_transform(v15, key_v20_parts[1], key_v20_parts[0], C_constants[1]))

    # 涉及 C1 (索引 0) 的操作
    # v15 在加密时是 = v17 + f(v16, k[3],k[2], C1)
    v17 = u32(v15 - f_transform(v16, key_v20_parts[3], key_v20_parts[2], C_constants[0])) # 这是原始的 X1 (输入右半块)
    # v16 在加密时是 = X0 + f(v17, k[1],k[0], C1)
    original_x0 = u32(v16 - f_transform(v17, key_v20_parts[1], key_v20_parts[0], C_constants[0])) # 这是原始的 X0 (输入左半块)
    
    original_x1 = v17

    return original_x0, original_x1

# --- 主解密过程 ---
decrypted_a1_dwords = []
# 成对处理加密后的DWORD (X0, X1)
for i in range(0, len(encrypted_dwords), 2):
    enc_x0 = encrypted_dwords[i]
    enc_x1 = encrypted_dwords[i+1]
    
    dec_x0, dec_x1 = decrypt_block_pair(enc_x0, enc_x1, v20_key, CONSTANTS_C)
    
    decrypted_a1_dwords.append(dec_x0)
    decrypted_a1_dwords.append(dec_x1)

# 将解密后的DWORD转换回字节数组
decrypted_a1_bytes = bytearray()
for dword_val in decrypted_a1_dwords:
    decrypted_a1_bytes.extend(struct.pack('<I', dword_val))

# --- 输出结果 ---
print("派生密钥 (v20) 的DWORD表示 (十六进制):")
print([hex(k) for k in v20_key])
print("\n加密后的DWORD (来自 byte_414060):")
print([hex(d) for d in encrypted_dwords])
print("\n解密后的 a1 的DWORD表示 (十六进制):")
print([hex(d) for d in decrypted_a1_dwords])
print("\n解密后的 a1 以十六进制字节序列表示:")
print(' '.join(f'{b:02X}' for b in decrypted_a1_bytes))
print("\n解密后的 a1 以ASCLL表示:")
print(decrypted_a1_bytes.decode('utf-8'))


