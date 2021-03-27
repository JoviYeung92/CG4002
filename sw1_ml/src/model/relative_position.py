# dancer1_position = position_model(in_data_dancer1)
# dancer2_position = position_model(in_data_dancer1)
# dancer3_position = position_model(in_data_dancer1)

def get_final_position(in_position='1 2 3', dancer1_move='none', dancer2_move='none', dancer3_move='none'):
    in_pos = in_position.split()
    in_pos = [int(i) for i in in_pos]
    d1, d2, d3 = in_pos
    out_pos = in_pos
    if dancer1_move == 'right' and dancer2_move == 'right' and dancer3_move == 'left':
        out_pos = [d3, d1, d2]
    elif dancer1_move == 'right' and dancer2_move == 'none' and dancer3_move == 'left':
        out_pos = [d3, d2, d1]
    elif dancer1_move == 'right' and dancer2_move == 'left' and dancer3_move == 'none':
        out_pos = [d2, d1, d3]
    elif dancer1_move == 'right' and dancer2_move == 'left' and dancer3_move == 'left':
        out_pos = [d2, d3, d1]
    elif dancer1_move == 'none' and dancer2_move == 'right' and dancer3_move == 'left':
        out_pos = [d1, d3, d2]
    else:
        out_pos = [d1, d2, d3]
        
    return ' '.join([str(i) for i in out_pos])
