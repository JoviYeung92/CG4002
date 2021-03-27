import os

def combine_dance_data(path):
    for person in os.listdir(path):
        print("Files read from ", person)
        dir_path = os.path.join(path, person)
        dance_moves = ['hair', 'rocket', 'zigzag', 'window', 'pushback', 'elbow', 'scarecrow', 'shoulder', 'logout']
        for dance_move in dance_moves:
            
            path1 = os.path.join(dir_path, dance_move + '.txt')
            if os.path.exists(path1):
                os.remove(path1)
            
            data = ""
            data1 = data2 = "" 
            
            with open(os.path.join(dir_path, dance_move + '0.txt')) as fp: 
                data = fp.read() 

            try:
                with open(os.path.join(dir_path, dance_move + '1.txt')) as fp: 
                    data1 = fp.read() 
            except: pass

            try:
                with open(os.path.join(dir_path, dance_move + '2.txt')) as fp: 
                    data2 = fp.read() 
            except: pass

            data += data1
            data += data2
   
            with open(path1, 'w') as fp: 
                fp.write(data)    
        
def pre_process_dance_data(path):
    for person in os.listdir(path):
        dir_path = os.path.join(path, person)
        dance_moves = ['hair.txt', 'rocket.txt', 'zigzag.txt', 'window.txt', 'pushback.txt', 'elbow.txt', 'scarecrow.txt', 'shoulder.txt', 'logout.txt']
        for dance_move in dance_moves:
            path1 = os.path.join(dir_path, dance_move)

            try:
                fp = open(path1, 'r')
                raw = fp.readlines()
                data = []

                for row in raw:
                    val = row.split()
                    
                    d = ''
                    req = [1, 3, 5, 7, 9, 11]
                    for index in req:
                        v = val[index]
                        v = v.replace('"', '')
                        v = v.replace(',', '')
                        d += v + ' '
                    data.append(d + '\n')
                    
                fp.close()
                os.remove(path1)
                
                fp = open(path1, 'a') 
                fp.writelines(data) 
            except: continue

def combine_all_dancer_data(path, folder1, folder2):
    dance_moves = ['hair.txt', 'rocket.txt', 'zigzag.txt', 'window.txt', 'pushback.txt', 'elbow.txt', 'scarecrow.txt', 'shoulder.txt', 'logout.txt']
    dance_dir = os.path.join(path, folder1)
    output_dir = os.path.join(path, folder2)
    for dance_move in dance_moves:
        data = ""
        for person in os.listdir(dance_dir):
            dir_path = os.path.join(dance_dir, person)
            path1 = os.path.join(dir_path, dance_move)
            
            try:
                with open(path1) as fp:
                    data += fp.read()
            except: continue

        with open(os.path.join(output_dir, dance_move), 'w') as fp:
            fp.write(data)

def pre_process_position_data(path):
    for person in os.listdir(path):
        dir_path = os.path.join(path, person)
        # dir_path = path
        position = ['left.txt', 'right.txt', 'none.txt']       
        for pos in position:
            path1 = os.path.join(dir_path, pos)
                        
            fp = open(path1, 'r')
            raw = fp.readlines()
            data = []

            for row in raw:
                val = row.split()
                
                d = ''
                req = [1, 3, 5, 7, 9, 11]
                for index in req:
                    v = val[index]
                    v = v.replace('"', '')
                    v = v.replace(',', '')
                    d += v + ' '
                data.append(d + '\n')

            fp.close()
            os.remove(path1)
            
            fp = open(path1, 'a') 
            fp.writelines(data)

def combine_all_position_data(path):
    position = ['left.txt', 'right.txt', 'none.txt']
    position_dir = os.path.join(path, 'position')
    output_dir = os.path.join(path, 'combined_position')
    for pos in position:
        data = ""
        for person in os.listdir(position_dir):
            dir_path = os.path.join(position_dir, person)
            path1 = os.path.join(dir_path, pos)
            
            with open(path1) as fp:
                data += fp.read()

        with open(os.path.join(output_dir, pos), 'w') as fp:
            fp.write(data)
