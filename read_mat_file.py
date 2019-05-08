import scipy.io

def return_classes(matfilepath):
    # Read in the mat file
    mat = scipy.io.loadmat(matfilepath)
    # extract list of labels
    labels = mat['cls_indexes']

    classes_list = []
    # loop through all elements
    for elem_arr in labels:
        # get the first entry (only contains one entry)
        elem = elem_arr[0]

        # add it to a list
        classes_list.append(elem)
    # print the list
    #print(classes_list)
    return classes_list

def main():

    file_path = '0000/000001-meta.mat'
    list = return_classes(file_path)
    print(list)

if __name__ == "__main__":
    main()