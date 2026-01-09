def convert_to_rub(row):
    '''Конвертация в рубли'''
    if row['salary.currency'] == 'EUR':
        return row['salary'] * 90
    if row['salary.currency'] == 'USD':
        return row['salary'] * 80
    return row['salary']


def convert_to_net(row):
    '''Конвертация в рубли'''
    if row['salary.gross'] == 1:
        return row['salary'] * 0.87
    return row['salary']
