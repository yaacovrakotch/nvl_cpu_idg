def create_txt_files(filename):
    with open(filename, 'r') as file:
        name_list =file.read().splitlines()

    for name in name_list:
        filename = name + ".permanent"
        with open(filename, 'w') as file:
            file.write(f'This is skip file for {name}.'.format(name))
        print("Created file:", filename)

filename = "name_list.list"
create_txt_files(filename)