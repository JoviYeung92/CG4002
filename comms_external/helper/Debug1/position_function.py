def get_final_position(in_position='1 2 3', dancer1move='none', dancer2move='none', dancer3move='none'):
        print(f"Previous Moves: {in_position} First move: {dancer1move}, Second Move: {dancer2move}, Third Move: {dancer3move}")
        in_pos = in_position.split()
        in_pos = [int(i) for i in in_pos]
        if len(in_pos) != 3:
            print('-----------------------------')
            print('Should never enter this state')
            print('-----------------------------')
            in_pos = [1, 2, 3]
        d1, d2, d3 = in_pos
        """
        Map d1, d2, d3 into the right variables dancer1_move, dancer2_move and dancer3_move
        For ex if d1, d2, d3 = 2, 3, 1 and initial dancer1_move = 'left', dancer2_move = 'right' and dancer3_move = 'none'
        map left, right, none to 2, 3, 1 that is right, none, left
        """
        if d1 == 1:
            dancer1_move = dancer1move
        elif d1 == 2:
            dancer1_move = dancer2move
        else:
            dancer1_move = dancer3move
        if d2 == 1:
            dancer2_move = dancer1move
        elif d2 == 2:
            dancer2_move = dancer2move
        else:
            dancer2_move = dancer3move
        if d3 == 1:
            dancer3_move = dancer1move
        elif d3 == 2:
            dancer3_move = dancer2move
        else:
            dancer3_move = dancer3move

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
        # if dancer1_move == 'right':
        #     if dancer2_move == 'right' and dancer3_move == 'left':
        #         out_pos = [d3, d1, d2]
        #     if dancer2_move == 'none' and dancer3_move == 'left':
        #         out_pos = [d3, d2, d1]
        #     if dancer2_move == 'left' and dancer3_move == 'none':
        #         out_pos = [d2, d1, d3]
        #     if dancer2_move == 'left' and dancer3_move == 'left':
        #         out_pos = [d2, d3, d1]
        #     else:
        #         val = random.random()
        #         if val < 0.25:
        #             out_pos = [d3, d1, d2]
        #         elif val < 0.5:
        #             out_pos = [d3, d2, d1]
        #         elif val < 0.75:
        #             out_pos = [d2, d1, d3]
        #         else:
        #             out_pos = [d2, d3, d1]
        # elif 
        # elif dancer1_move == 'right' and dancer2_move == 'none' and dancer3_move == 'left':
        #     out_pos = [d3, d2, d1]
        # elif dancer1_move == 'right' and dancer2_move == 'left' and dancer3_move == 'none':
        #     out_pos = [d2, d1, d3]
        # elif dancer1_move == 'right' and dancer2_move == 'left' and dancer3_move == 'left':
        #     out_pos = [d2, d3, d1]
        # elif dancer1_move == 'none' and dancer2_move == 'right' and dancer3_move == 'left':
        #     out_pos = [d1, d3, d2]
        # else:
        #     out_pos = [d1, d2, d3]
        string_to_return = ' '.join([str(i) for i in out_pos])
        print(f"THE POSITION RETURNED BY SHREYAS FUNCTION: {string_to_return}")
        return string_to_return

def main():
    while True:
        x = input("Please enter previous positions\n")
        a = input("Enter dancer 1 move\n")
        b = input("Enter dancer 2 move\n")
        c = input("Enter dancer 3 move\n")
        result = get_final_position(x, a, b, c)
        print(result)

if __name__ == "__main__":
    main()

"""
Test cases
1. 2 3 1 -> left right, none -> 1 3 2
2. 3 2 1 -> left none right -> 1 2 3
3. 1 3 2 -> none none none -> 1 3 2
4. 1 3 2 -> none left right -> 1 2 3
5. 3 2 1 -> left left right ->  2 1 3
"""
