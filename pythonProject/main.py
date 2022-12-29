

from sqlite3 import *
import pandas as pd
import requests
import PySimpleGUI as sg

def randomTokens(dataframe):
    cols = ['UID', 'TZ', 'PhoneNumWork', 'PhoneNumNayad', 'PhoneNumHome', 'Email', 'Address']

    for c in cols:
        a = dataframe[c]
        a = a.sample(frac=1)
        a.reset_index(inplace=True, drop=True)
        dataframe[c] = a
    return dataframe


def execute_values(d_secure, df, table):
    # if table == 'employees_no_sec':
    #     df = randomTokens(df)
    tuples = [tuple(x) for x in df.to_numpy()]
    cols = ','.join(list(df.columns))
    # SQL query to execute
    query = "DELETE FROM "+table
    cursor = d_secure.cursor()
    cursor.execute(query)

    query = "INSERT INTO %s(%s) VALUES %s" % (table, cols, tuples)
    query = query.replace('[', '')
    query = query.replace(']', '')
    query = query.replace('None', 'null')
    query = query.replace('nan', 'null')
    cursor = d_secure.cursor()
    cursor.execute(query)


def insertToTree(table_name, firstname, lastname):
    curs = db_conn.cursor()
    db = "select * from "+table_name+" where FName like '%"+firstname+"%' and LName like '%"+lastname+"%' "
    curs.execute(db)
    result = curs.fetchall()
    # df = pd.DataFrame(result)
    # df = randomTokens(df)
    return result


def connect_error():
    error_ = [
        [
            sg.Text("You do not have permissions to execute")
        ]
    ]

    layout_error = [
        [
            sg.Column(error_),
            sg.VSeperator(),
        ]
    ]

    window_er = sg.Window("Error", layout_error, icon=icon)

    while True:
        event, values = window_er.read()
        if event == sg.WIN_CLOSED:
            break

        window_er.close()


def connect_app():

    file_list_column1 = [
        [
            sg.Text("User name",key='U'),
            sg.In(size=(25, 1), enable_events=True, key="Uname"),
            # sg.Button("Search")
        ],
        [
            sg.Text("Password ",key='P'),
            sg.In(size=(25, 1), enable_events=True, key="Upass",password_char='*'),
        ],
        [sg.Button("OK")]
    ]
    layout = [
        [
            sg.Column(file_list_column1),
            sg.VSeperator(),
        ]
    ]

    window_conn = sg.Window("CONNECT", layout, icon=icon)
    Permission = None
    while True:
        event, values = window_conn.read()

        if event == "OK" and str(values['Uname']) == 'DBA' and str(values['Upass']) == '123':
            Permission = 1
            break

        elif event == "OK" and str(values['Uname']) != '':
            Permission = 0
            break

        elif event == "OK":
            window_conn['U'].update(text_color='red')

        if event == sg.WIN_CLOSED:
            break

    window_conn.close()
    return Permission, str(values['Uname'])

if __name__ == '__main__':

    icon = r'.\ICON.ico'

    prodPermission, loginUser = connect_app()
    if prodPermission != 0 and prodPermission != 1:
        exit()

    table_no_sec = 'employees_no_sec'
    table_sec = 'employees_sec'

    url = "https://0yes9cjw1k.execute-api.eu-central-1.amazonaws.com/prodSearch/search///0"
    resp = requests.get(url)
    data = resp.json()
    df_no_sec = pd.DataFrame.from_records(data)

    url = "https://0yes9cjw1k.execute-api.eu-central-1.amazonaws.com/prodSearch/search///1"
    resp = requests.get(url)
    data = resp.json()
    df_sec = pd.DataFrame.from_records(data)

    db_conn = connect("data1.db")
    curs1 = db_conn.cursor()
    db1 = "drop table "+table_no_sec
    db2 = "drop table "+table_sec

    try:
        curs1.execute(db1)
        curs1.execute(db2)
    except:
        ''
    db1 = "create table "+table_no_sec+"(ID int, UID text, TZ text, FName text, LName text, PhoneNumWork text, PhoneNumNayad text, " \
         "PhoneNumHome text, Email text, Address text, MangerID int)"
    db2 = "create table "+table_sec+"(ID int, UID text, TZ text, FName text, LName text, PhoneNumWork text, PhoneNumNayad text, " \
         "PhoneNumHome text, Email text, Address text, MangerID int)"
    curs1.execute(db1)
    curs1.execute(db2)

    execute_values(db_conn, df_no_sec, table_no_sec)
    execute_values(db_conn, df_sec, table_sec)

    data_values = insertToTree(table_no_sec, '', '')

    data_headings = ['ID', 'UID', 'TZ', 'First Name', 'Last Name', 'PhoneNumWork', 'PhoneNumNayad', 'PhoneNumHome', 'Email', 'Address', 'MangerID']
    data_values.append(['', '', '', ''])
    data_cols_width = [6, 16, 16, 13, 13, 16, 16, 16, 20, 20, 7]

    file_list_column = [
        [
            sg.Text("First name"),
            sg.In(size=(25, 1), enable_events=True, key="Fname"),
            sg.Push(),
            sg.Text("Wellcome "+loginUser, key="wellcome", text_color='black', auto_size_text=True),
        ],
        [
            sg.Text("Last name"),
            sg.In(size=(25, 1), enable_events=True, key="Lname"),
            sg.Push(),
            sg.Button("Change User"),
        ],
        [sg.Table(values=data_values, headings=data_headings,
                  max_col_width=65,
                  col_widths=data_cols_width,
                  auto_size_columns=False,
                  justification='left',
                  enable_events=False,
                  expand_x=False,
                  expand_y=True,
                  selected_row_colors='red on yellow',
                  vertical_scroll_only=True,
                  enable_click_events=False,
                  num_rows=35, key='Emp_Table',
                  )
         ],
        [

            sg.Button("Prod"),
            sg.Button("Test"),
            sg.Push(),
            sg.Button("Exit"),

        ]
    ]

    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
        ]
    ]

    main_window = sg.Window("Find Employees", layout, icon=icon)

    while True:
        event, values = main_window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break

        if event == "Prod" and prodPermission:
            data_values = insertToTree(table_sec, str(values['Fname']), str(values['Lname']))
            main_window['Emp_Table'].update(values=data_values)

        elif event == "Prod" and prodPermission == 0:
            connect_error()

        elif event == "Change User":
            prodPermission, loginUser = connect_app()
            main_window['wellcome'].update("Wellcome "+loginUser)

        else:
            execute_values(db_conn, randomTokens(df_no_sec), table_no_sec)
            data_values = insertToTree(table_no_sec, str(values['Fname']), str(values['Lname']))
            main_window['Emp_Table'].update(values=data_values)

    main_window.close()







