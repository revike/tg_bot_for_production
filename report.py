from pandas import DataFrame, ExcelWriter


def to_excel(data, user, file):
    """Report to excel"""
    data_frame = DataFrame(data)
    user_frame = DataFrame(user)

    sheet_name = ''.join(user[0][1].split(' '))
    writer = ExcelWriter(f'reports/{file}.xlsx', engine='xlsxwriter')
    data_frame_group = data_frame.groupby(
        ['Продукт', 'Операция', 'Цех', 'Цена'])['Количество'].sum().reset_index()
    data_frame_group.to_excel(
        writer, sheet_name=sheet_name,
        columns=['Продукт', 'Операция', 'Цех', 'Цена', 'Количество'],
        header=True, index=False, startrow=4, startcol=1,
        freeze_panes=[5, 1]
    )
    user_frame.to_excel(
        writer, sheet_name=sheet_name,
        header=False, index=False, startrow=1, startcol=1,
    )
    sheet = writer.sheets[sheet_name]
    sheet.conditional_format('C3:C3', {'type': '3_color_scale'})
    sheet.set_column(5, 1, 30)

    writer.save()


def one_file_excel(file_name, sheet_name:list, data: list):
    """Write all data in one file"""
    writer = ExcelWriter(f'reports/Отчет - {file_name}.xlsx', engine='xlsxwriter')
    i = len(sheet_name)
    while i >= 0:
        data[i-1].to_excel(
            writer, sheet_name=sheet_name[i-1],
            header=False, index=False, startrow=1, startcol=0,
            freeze_panes=[5, 1]
        )
        sheet = writer.sheets[sheet_name[i-1]]
        sheet.conditional_format('C3:C3', {'type': '3_color_scale'})
        sheet.set_column(5, 1, 30)
        i -= 1
    writer.save()
