def compare_two_lists(list1: list, list2: list) -> list:
    list_of_all_values = [value for element in list1
                          for value in element.values()]
    not_in_list = []
    for t in list2:
        if t not in list_of_all_values:
            not_in_list.append(t)
    return not_in_list
