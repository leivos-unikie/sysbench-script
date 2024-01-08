def extract(file, detect_str, str1, str2):

    #file_name = r'578_cpu_report'
    file_name = file

    with open(file_name, 'r') as fp:

        # read all lines using readline()
        lines = fp.readlines()
        for row in lines:

            # find() method returns -1 if the value is not found,
            # if found it returns index of the first occurrence of the substring
            if row.find(detect_str) != -1:

                # getting index of substrings
                idx1 = row.index(str1)
                idx2 = row.index(str2)

                # print(idx1)
                # print(idx2)

                res = ''
                # getting elements in between
                for idx in range(idx1 + len(str1), idx2):
                    res = res + row[idx]

                # print("The extracted string : " + res)

                return res